import asyncio
import hmac
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit

import httpx
from docker.errors import DockerException
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.config import Settings
from app.ai_pack import AIPackInstallError, AIPackInstaller
from app.docker_update import ContainerUpdateError, QuantumContainerUpdater
from app.releases import GitHubReleaseClient, UpdateVerificationError


logger = logging.getLogger(__name__)
settings = Settings.from_env()
settings.validate()
security = HTTPBasic()
app = FastAPI(title="Multiverse Quantum OS Updater", docs_url=None, redoc_url=None)
AUDIT_LOG = Path("/var/lib/quantum-updater/audit.jsonl")
UPDATE_LOCK = asyncio.Lock()
AI_INSTALL_LOCK = asyncio.Lock()


def audit(event: str, **details: object) -> None:
    record = {
        "timestamp": datetime.now(UTC).isoformat(),
        "event": event,
        **details,
    }
    with AUDIT_LOG.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True) + "\n")


def authenticate(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    valid_user = hmac.compare_digest(credentials.username, "admin")
    valid_password = hmac.compare_digest(
        credentials.password, settings.admin_password
    )
    if not (valid_user and valid_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def require_same_origin(request: Request) -> None:
    fetch_site = request.headers.get("sec-fetch-site")
    if fetch_site not in {None, "same-origin", "none"}:
        raise HTTPException(status_code=403, detail="Cross-site request rejected")
    origin = request.headers.get("origin")
    if origin and urlsplit(origin).netloc != request.headers.get("host"):
        raise HTTPException(status_code=403, detail="Origin does not match host")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
async def index(_: str = Depends(authenticate)) -> str:
    return """<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport"
content="width=device-width,initial-scale=1"><title>Quantum OS Update</title>
<style>
body{margin:0;background:#080b14;color:#eef3ff;font:16px system-ui}
main{max-width:760px;margin:8vh auto;padding:28px}article{padding:28px;
border:1px solid #35405a;border-radius:18px;background:#111729}
h1{font-size:2.4rem;margin:.2em 0}.tag{color:#63f2d0;font:700 12px monospace}
button{padding:12px 18px;border:0;border-radius:9px;background:#63f2d0;
font-weight:800;cursor:pointer;margin-right:8px}pre{padding:15px;background:#090d18;
white-space:pre-wrap;border-radius:9px;color:#b9c5d8}.warn{color:#ffc98a}
</style></head><body><main><article><span class="tag">SIGNED GITHUB RELEASES</span>
<h1>Multiverse Quantum OS Updater</h1><p>署名、リポジトリ、イメージ、
SHA-256ダイジェストを検証してから更新します。</p>
<p class="warn">更新すると実行中のJupyterセッションが再起動します。</p>
<button onclick="callApi('/api/check')">更新を確認</button>
<button onclick="applyUpdate()">署名済み更新を適用</button>
<hr style="border-color:#35405a;margin:24px 0">
<h2>AI拡張パック</h2><p>説明可能AIカーネルを隔離ボリュームへ導入します。</p>
<button onclick="callApi('/api/ai/check')">AIパックを確認</button>
<button onclick="installAI()">署名済みAIを導入</button>
<pre id="output">準備完了</pre></article></main><script>
async function callApi(url,options={}){const out=document.querySelector('#output');
out.textContent='処理中…';const response=await fetch(url,options);const data=await
response.json();out.textContent=JSON.stringify(data,null,2);return response}
async function applyUpdate(){if(!confirm('量子OSを再起動して更新しますか？'))return;
await callApi('/api/apply',{method:'POST',headers:{'Content-Type':'application/json'},
body:'{}'})}
async function installAI(){if(!confirm('署名済みAI拡張を導入しますか？'))return;
await callApi('/api/ai/install',{method:'POST',headers:{'Content-Type':'application/json'},
body:'{}'})}</script></body></html>"""


@app.get("/api/status")
async def updater_status(_: str = Depends(authenticate)) -> dict:
    try:
        current = await asyncio.to_thread(QuantumContainerUpdater().current)
    except (DockerException, ContainerUpdateError) as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return {"current": current, "checked_at": datetime.now(UTC).isoformat()}


@app.get("/api/check")
async def check_update(_: str = Depends(authenticate)) -> dict:
    try:
        release = await GitHubReleaseClient(settings).latest()
        current = await asyncio.to_thread(QuantumContainerUpdater().current)
    except (httpx.HTTPError, UpdateVerificationError) as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    except (DockerException, ContainerUpdateError) as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    audit("update_checked", release=release.tag, image=release.image_reference)
    return {
        "release": release.tag,
        "image": release.image_reference,
        "published_at": release.published_at,
        "current": current,
    }


@app.post("/api/apply")
async def apply_update(
    _: str = Depends(authenticate),
    __: None = Depends(require_same_origin),
) -> dict:
    async with UPDATE_LOCK:
        try:
            release = await GitHubReleaseClient(settings).latest()
            result = await asyncio.to_thread(
                QuantumContainerUpdater().apply, release
            )
        except (httpx.HTTPError, UpdateVerificationError) as error:
            raise HTTPException(status_code=502, detail=str(error)) from error
        except (DockerException, ContainerUpdateError) as error:
            logger.exception("Quantum OS update failed")
            audit("update_failed", error=type(error).__name__)
            raise HTTPException(status_code=503, detail=str(error)) from error
    logger.info("Applied signed Quantum OS release %s", release.tag)
    audit("update_applied", release=release.tag, image=release.image_reference)
    return {"updated": True, "release": release.tag, "container": result}


@app.get("/api/ai/status")
async def ai_status(_: str = Depends(authenticate)) -> dict:
    try:
        installed = await asyncio.to_thread(AIPackInstaller().status)
    except (DockerException, AIPackInstallError) as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return {"installed": installed}


@app.get("/api/ai/check")
async def check_ai_pack(_: str = Depends(authenticate)) -> dict:
    try:
        release = await GitHubReleaseClient(settings).latest_ai_pack()
        installed = await asyncio.to_thread(AIPackInstaller().status)
    except (httpx.HTTPError, UpdateVerificationError) as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    except (DockerException, AIPackInstallError) as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    audit("ai_pack_checked", release=release.tag, image=release.image_reference)
    return {
        "release": release.tag,
        "package_id": release.package_id,
        "version": release.version,
        "image": release.image_reference,
        "published_at": release.published_at,
        "installed": installed,
    }


@app.post("/api/ai/install")
async def install_ai_pack(
    _: str = Depends(authenticate),
    __: None = Depends(require_same_origin),
) -> dict:
    async with AI_INSTALL_LOCK:
        try:
            release = await GitHubReleaseClient(settings).latest_ai_pack()
            result = await asyncio.to_thread(AIPackInstaller().install, release)
        except (httpx.HTTPError, UpdateVerificationError) as error:
            raise HTTPException(status_code=502, detail=str(error)) from error
        except (DockerException, AIPackInstallError) as error:
            logger.exception("AI pack installation failed")
            audit("ai_pack_failed", error=type(error).__name__)
            raise HTTPException(status_code=503, detail=str(error)) from error
    audit("ai_pack_installed", release=release.tag, version=release.version)
    return {"installed": True, "package": result}
