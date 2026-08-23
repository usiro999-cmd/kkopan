import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    repository: str
    tag_prefix: str
    image_prefix: str
    public_key: str
    admin_password: str
    github_token: str
    ai_pack_tag_prefix: str
    ai_pack_image_prefix: str

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            repository=os.environ.get(
                "UPDATE_REPOSITORY", "usiro999-cmd/kkopan"
            ),
            tag_prefix=os.environ.get("UPDATE_TAG_PREFIX", "quantum-os-v"),
            image_prefix=os.environ.get(
                "UPDATE_IMAGE_PREFIX",
                "ghcr.io/usiro999-cmd/kkopan/quantum-os",
            ),
            public_key=os.environ.get("UPDATE_PUBLIC_KEY", ""),
            admin_password=os.environ.get("UPDATE_ADMIN_PASSWORD", ""),
            github_token=os.environ.get("GITHUB_TOKEN", ""),
            ai_pack_tag_prefix=os.environ.get(
                "AI_PACK_TAG_PREFIX", "quantum-ai-v"
            ),
            ai_pack_image_prefix=os.environ.get(
                "AI_PACK_IMAGE_PREFIX",
                "ghcr.io/usiro999-cmd/kkopan/quantum-ai-pack",
            ),
        )

    def validate(self) -> None:
        if "/" not in self.repository or self.repository.count("/") != 1:
            raise ValueError("UPDATE_REPOSITORY must use owner/repository format")
        if not self.image_prefix.startswith("ghcr.io/"):
            raise ValueError("UPDATE_IMAGE_PREFIX must use ghcr.io")
        if not self.ai_pack_image_prefix.startswith("ghcr.io/"):
            raise ValueError("AI_PACK_IMAGE_PREFIX must use ghcr.io")
        if len(self.admin_password) < 16:
            raise ValueError("UPDATE_ADMIN_PASSWORD must be at least 16 characters")
