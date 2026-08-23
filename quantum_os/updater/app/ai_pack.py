import json
from pathlib import Path

import docker
from docker.errors import APIError, ContainerError

from app.releases import VerifiedAIPack


AI_VOLUME_LABEL = "com.multiverse.quantum-os.ai-packs"
STATE_FILE = Path("/var/lib/quantum-updater/ai-pack.json")


class AIPackInstallError(RuntimeError):
    pass


class AIPackInstaller:
    def __init__(self):
        self.client = docker.from_env()

    def status(self) -> dict | None:
        if not STATE_FILE.exists():
            return None
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise AIPackInstallError("AI pack state is corrupted") from error

    def install(self, release: VerifiedAIPack) -> dict:
        volume = self._ai_volume()
        self.client.images.pull(release.image_reference)
        try:
            output = self.client.containers.run(
                release.image_reference,
                remove=True,
                network_disabled=True,
                environment={"AI_PACK_VERSION": release.version},
                volumes={volume.name: {"bind": "/target", "mode": "rw"}},
                read_only=True,
                cap_drop=["ALL"],
                security_opt=["no-new-privileges:true"],
                tmpfs={"/tmp": "size=64m,mode=1777"},
            )
        except (APIError, ContainerError) as error:
            raise AIPackInstallError("AI pack installer failed") from error
        state = {
            "package_id": release.package_id,
            "version": release.version,
            "release": release.tag,
            "image": release.image_reference,
            "installer_output": output.decode("utf-8", errors="replace").strip(),
        }
        temporary = STATE_FILE.with_suffix(".tmp")
        temporary.write_text(json.dumps(state, sort_keys=True), encoding="utf-8")
        temporary.replace(STATE_FILE)
        return state

    def _ai_volume(self):
        volumes = self.client.volumes.list(
            filters={"label": f"{AI_VOLUME_LABEL}=true"}
        )
        if len(volumes) != 1:
            raise AIPackInstallError(
                "Exactly one managed AI pack volume is required"
            )
        return volumes[0]
