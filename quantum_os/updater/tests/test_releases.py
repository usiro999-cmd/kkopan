import base64
import asyncio
import json

import pytest
from nacl.signing import SigningKey

from app.config import Settings
from app import releases as release_module
from app.releases import (
    GitHubReleaseClient,
    UpdateVerificationError,
    verify_ai_pack_manifest,
    verify_manifest,
)


def settings(public_key: str) -> Settings:
    return Settings(
        repository="usiro999-cmd/kkopan",
        tag_prefix="quantum-os-v",
        image_prefix="ghcr.io/usiro999-cmd/kkopan/quantum-os",
        public_key=public_key,
        admin_password="a-secure-test-password",
        github_token="",
        ai_pack_tag_prefix="quantum-ai-v",
        ai_pack_image_prefix=(
            "ghcr.io/usiro999-cmd/kkopan/quantum-ai-pack"
        ),
    )


def signed_manifest():
    signing_key = SigningKey.generate()
    manifest = json.dumps(
        {
            "schema_version": 1,
            "release": "quantum-os-v1.0.0",
            "repository": "usiro999-cmd/kkopan",
            "image": "ghcr.io/usiro999-cmd/kkopan/quantum-os",
            "digest": "sha256:" + "a" * 64,
            "published_at": "2026-08-23T00:00:00Z",
        },
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    signature = base64.b64encode(signing_key.sign(manifest).signature)
    public_key = base64.b64encode(bytes(signing_key.verify_key)).decode()
    return manifest, signature, public_key


def test_accepts_valid_signed_allowlisted_manifest():
    manifest, signature, public_key = signed_manifest()
    release = verify_manifest(
        manifest, signature, "quantum-os-v1.0.0", settings(public_key)
    )
    assert release.image_reference.endswith("@" + "sha256:" + "a" * 64)


def test_rejects_modified_manifest():
    manifest, signature, public_key = signed_manifest()
    modified = manifest.replace(b"1.0.0", b"9.0.0")
    with pytest.raises(UpdateVerificationError, match="signature"):
        verify_manifest(
            modified, signature, "quantum-os-v9.0.0", settings(public_key)
        )


def test_rejects_non_allowlisted_image():
    manifest, signature, public_key = signed_manifest()
    signing_key = SigningKey.generate()
    malicious = manifest.replace(
        b"ghcr.io/usiro999-cmd/kkopan/quantum-os",
        b"ghcr.io/attacker/quantum-os",
    )
    malicious_signature = base64.b64encode(
        signing_key.sign(malicious).signature
    )
    attacker_public_key = base64.b64encode(
        bytes(signing_key.verify_key)
    ).decode()
    with pytest.raises(UpdateVerificationError, match="allow-listed"):
        verify_manifest(
            malicious,
            malicious_signature,
            "quantum-os-v1.0.0",
            settings(attacker_public_key),
        )


def test_accepts_signed_ai_pack_manifest():
    signing_key = SigningKey.generate()
    manifest = json.dumps(
        {
            "schema_version": 1,
            "release": "quantum-ai-v1.0.0",
            "repository": "usiro999-cmd/kkopan",
            "package_id": "multiverse-explainable-ai",
            "version": "1.0.0",
            "image": "ghcr.io/usiro999-cmd/kkopan/quantum-ai-pack",
            "digest": "sha256:" + "b" * 64,
            "published_at": "2026-08-23T00:00:00Z",
        },
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    signature = base64.b64encode(signing_key.sign(manifest).signature)
    public_key = base64.b64encode(bytes(signing_key.verify_key)).decode()
    release = verify_ai_pack_manifest(
        manifest,
        signature,
        "quantum-ai-v1.0.0",
        settings(public_key),
    )
    assert release.package_id == "multiverse-explainable-ai"
    assert release.version == "1.0.0"


def test_rejects_signed_unapproved_ai_package():
    signing_key = SigningKey.generate()
    manifest = json.dumps(
        {
            "schema_version": 1,
            "release": "quantum-ai-v1.0.0",
            "repository": "usiro999-cmd/kkopan",
            "package_id": "unapproved-ai",
            "version": "1.0.0",
            "image": "ghcr.io/usiro999-cmd/kkopan/quantum-ai-pack",
            "digest": "sha256:" + "c" * 64,
            "published_at": "2026-08-23T00:00:00Z",
        },
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    signature = base64.b64encode(signing_key.sign(manifest).signature)
    public_key = base64.b64encode(bytes(signing_key.verify_key)).decode()
    with pytest.raises(UpdateVerificationError, match="package ID"):
        verify_ai_pack_manifest(
            manifest,
            signature,
            "quantum-ai-v1.0.0",
            settings(public_key),
        )


def test_release_client_paginates_and_enables_redirects(monkeypatch):
    signing_key = SigningKey.generate()
    public_key = base64.b64encode(bytes(signing_key.verify_key)).decode()
    manifest = json.dumps(
        {
            "schema_version": 1,
            "release": "quantum-ai-v1.0.0",
            "repository": "usiro999-cmd/kkopan",
            "package_id": "multiverse-explainable-ai",
            "version": "1.0.0",
            "image": "ghcr.io/usiro999-cmd/kkopan/quantum-ai-pack",
            "digest": "sha256:" + "d" * 64,
            "published_at": "2026-08-23T00:00:00Z",
        },
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    signature = base64.b64encode(signing_key.sign(manifest).signature)
    constructor_options = {}

    class Response:
        def __init__(self, payload=None, content=b""):
            self.payload = payload
            self.content = content

        def raise_for_status(self):
            return None

        def json(self):
            return self.payload

    class Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_):
            return None

        async def get(self, url, params=None, headers=None):
            if params == {"per_page": 100, "page": 1}:
                return Response(
                    [
                        {
                            "draft": False,
                            "prerelease": False,
                            "tag_name": f"other-v{index}",
                            "assets": [],
                        }
                        for index in range(100)
                    ]
                )
            if params == {"per_page": 100, "page": 2}:
                return Response(
                    [
                        {
                            "draft": False,
                            "prerelease": False,
                            "tag_name": "quantum-ai-v1.0.0",
                            "assets": [
                                {
                                    "name": "quantum-ai-pack.json",
                                    "url": "https://api.github.test/manifest",
                                },
                                {
                                    "name": "quantum-ai-pack.sig",
                                    "url": "https://api.github.test/signature",
                                },
                            ],
                        }
                    ]
                )
            if url.endswith("/manifest"):
                return Response(content=manifest)
            if url.endswith("/signature"):
                return Response(content=signature)
            raise AssertionError(f"unexpected request: {url} {params}")

    def client_factory(**options):
        constructor_options.update(options)
        return Client()

    monkeypatch.setattr(release_module.httpx, "AsyncClient", client_factory)
    release = asyncio.run(GitHubReleaseClient(settings(public_key)).latest_ai_pack())
    assert release.version == "1.0.0"
    assert constructor_options["follow_redirects"] is True
