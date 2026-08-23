import base64
import json
import re
from dataclasses import dataclass

import httpx
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

from app.config import Settings


DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
VERSION_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")


class UpdateVerificationError(RuntimeError):
    pass


@dataclass(frozen=True)
class VerifiedRelease:
    tag: str
    image: str
    digest: str
    published_at: str

    @property
    def image_reference(self) -> str:
        return f"{self.image}@{self.digest}"


@dataclass(frozen=True)
class VerifiedAIPack:
    tag: str
    package_id: str
    version: str
    image: str
    digest: str
    published_at: str

    @property
    def image_reference(self) -> str:
        return f"{self.image}@{self.digest}"


class GitHubReleaseClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "multiverse-quantum-os-updater",
        }
        if self.settings.github_token:
            headers["Authorization"] = f"Bearer {self.settings.github_token}"
        return headers

    async def latest(self) -> VerifiedRelease:
        release, manifest, signature = await self._latest_assets(
            self.settings.tag_prefix,
            "quantum-os-update.json",
            "quantum-os-update.sig",
        )
        return verify_manifest(
            manifest,
            signature,
            release["tag_name"],
            self.settings,
        )

    async def latest_ai_pack(self) -> VerifiedAIPack:
        release, manifest, signature = await self._latest_assets(
            self.settings.ai_pack_tag_prefix,
            "quantum-ai-pack.json",
            "quantum-ai-pack.sig",
        )
        return verify_ai_pack_manifest(
            manifest,
            signature,
            release["tag_name"],
            self.settings,
        )

    async def _latest_assets(
        self, tag_prefix: str, manifest_name: str, signature_name: str
    ) -> tuple[dict, bytes, bytes]:
        base_url = (
            f"https://api.github.com/repos/{self.settings.repository}/releases"
        )
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            release = None
            for page in range(1, 11):
                response = await client.get(
                    base_url,
                    params={"per_page": 100, "page": page},
                    headers=self.headers,
                )
                response.raise_for_status()
                releases = response.json()
                release = next(
                    (
                        item
                        for item in releases
                        if not item["draft"]
                        and not item["prerelease"]
                        and item["tag_name"].startswith(tag_prefix)
                    ),
                    None,
                )
                if release is not None or len(releases) < 100:
                    break
            if release is None:
                raise UpdateVerificationError("No matching stable release found")
            assets = {asset["name"]: asset for asset in release["assets"]}
            try:
                manifest_asset = assets[manifest_name]
                signature_asset = assets[signature_name]
            except KeyError as error:
                raise UpdateVerificationError(
                    "Release is missing signed update assets"
                ) from error
            manifest = await self._download(client, manifest_asset["url"])
            signature = await self._download(client, signature_asset["url"])
        return release, manifest, signature

    async def _download(self, client: httpx.AsyncClient, url: str) -> bytes:
        headers = dict(self.headers)
        headers["Accept"] = "application/octet-stream"
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        if len(response.content) > 64_000:
            raise UpdateVerificationError("Update asset is too large")
        return response.content


def verify_manifest(
    manifest_bytes: bytes,
    signature_bytes: bytes,
    release_tag: str,
    settings: Settings,
) -> VerifiedRelease:
    if not settings.public_key:
        raise UpdateVerificationError("UPDATE_PUBLIC_KEY is not configured")
    try:
        verify_key = VerifyKey(base64.b64decode(settings.public_key, validate=True))
        signature = base64.b64decode(signature_bytes.strip(), validate=True)
        verify_key.verify(manifest_bytes, signature)
    except (ValueError, BadSignatureError) as error:
        raise UpdateVerificationError("Invalid update signature") from error
    try:
        manifest = json.loads(manifest_bytes)
    except json.JSONDecodeError as error:
        raise UpdateVerificationError("Invalid update manifest JSON") from error
    expected_keys = {
        "schema_version",
        "release",
        "repository",
        "image",
        "digest",
        "published_at",
    }
    if set(manifest) != expected_keys or manifest["schema_version"] != 1:
        raise UpdateVerificationError("Unsupported update manifest schema")
    if manifest["release"] != release_tag:
        raise UpdateVerificationError("Release tag does not match manifest")
    if manifest["repository"] != settings.repository:
        raise UpdateVerificationError("Repository is not allow-listed")
    if manifest["image"] != settings.image_prefix:
        raise UpdateVerificationError("Image is not allow-listed")
    if not DIGEST_PATTERN.fullmatch(manifest["digest"]):
        raise UpdateVerificationError("Image digest is invalid")
    return VerifiedRelease(
        tag=release_tag,
        image=manifest["image"],
        digest=manifest["digest"],
        published_at=manifest["published_at"],
    )


def verify_ai_pack_manifest(
    manifest_bytes: bytes,
    signature_bytes: bytes,
    release_tag: str,
    settings: Settings,
) -> VerifiedAIPack:
    manifest = _verify_signed_json(manifest_bytes, signature_bytes, settings)
    expected_keys = {
        "schema_version",
        "release",
        "repository",
        "package_id",
        "version",
        "image",
        "digest",
        "published_at",
    }
    if set(manifest) != expected_keys or manifest["schema_version"] != 1:
        raise UpdateVerificationError("Unsupported AI pack manifest schema")
    if manifest["release"] != release_tag:
        raise UpdateVerificationError("Release tag does not match AI pack")
    if manifest["repository"] != settings.repository:
        raise UpdateVerificationError("AI pack repository is not allow-listed")
    if manifest["package_id"] != "multiverse-explainable-ai":
        raise UpdateVerificationError("AI package ID is not allow-listed")
    if manifest["image"] != settings.ai_pack_image_prefix:
        raise UpdateVerificationError("AI pack image is not allow-listed")
    if not VERSION_PATTERN.fullmatch(manifest["version"]):
        raise UpdateVerificationError("AI pack version is invalid")
    if not DIGEST_PATTERN.fullmatch(manifest["digest"]):
        raise UpdateVerificationError("AI pack digest is invalid")
    return VerifiedAIPack(
        tag=release_tag,
        package_id=manifest["package_id"],
        version=manifest["version"],
        image=manifest["image"],
        digest=manifest["digest"],
        published_at=manifest["published_at"],
    )


def _verify_signed_json(
    manifest_bytes: bytes, signature_bytes: bytes, settings: Settings
) -> dict:
    if not settings.public_key:
        raise UpdateVerificationError("UPDATE_PUBLIC_KEY is not configured")
    try:
        verify_key = VerifyKey(base64.b64decode(settings.public_key, validate=True))
        signature = base64.b64decode(signature_bytes.strip(), validate=True)
        verify_key.verify(manifest_bytes, signature)
    except (ValueError, BadSignatureError) as error:
        raise UpdateVerificationError("Invalid update signature") from error
    try:
        return json.loads(manifest_bytes)
    except json.JSONDecodeError as error:
        raise UpdateVerificationError("Invalid update manifest JSON") from error
