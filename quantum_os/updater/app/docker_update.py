import time

import docker
from docker.errors import APIError, NotFound

from app.releases import VerifiedRelease


MANAGED_LABEL = "com.multiverse.quantum-os.managed"


class ContainerUpdateError(RuntimeError):
    pass


class QuantumContainerUpdater:
    def __init__(self):
        self.client = docker.from_env()

    def current(self) -> dict[str, str]:
        container = self._managed_container()
        return {
            "container": container.name,
            "image": container.attrs["Config"]["Image"],
            "status": container.status,
        }

    def apply(self, release: VerifiedRelease) -> dict[str, str]:
        old = self._managed_container()
        original_name = old.name
        backup_name = f"{original_name}-rollback-{int(time.time())}"
        self.client.images.pull(release.image_reference)
        old.reload()
        config = old.attrs["Config"]
        host = old.attrs["HostConfig"]
        networks = list(old.attrs["NetworkSettings"]["Networks"])
        volumes = {
            mount["Source"]: {
                "bind": mount["Destination"],
                "mode": "rw" if mount.get("RW", False) else "ro",
            }
            for mount in old.attrs["Mounts"]
            if mount["Type"] in {"bind", "volume"}
        }
        old.stop(timeout=30)
        old.rename(backup_name)
        replacement = None
        try:
            replacement = self.client.containers.create(
                release.image_reference,
                name=original_name,
                command=config.get("Cmd"),
                entrypoint=config.get("Entrypoint"),
                environment=config.get("Env"),
                labels=config.get("Labels"),
                user=config.get("User"),
                working_dir=config.get("WorkingDir"),
                ports=host.get("PortBindings"),
                volumes=volumes,
                restart_policy=host.get("RestartPolicy"),
                security_opt=host.get("SecurityOpt"),
                cap_drop=host.get("CapDrop"),
                tmpfs=host.get("Tmpfs"),
                healthcheck=config.get("Healthcheck"),
                network=networks[0] if networks else None,
                detach=True,
            )
            for network in networks[1:]:
                self.client.networks.get(network).connect(replacement)
            replacement.start()
            self._wait_healthy(replacement)
            old.remove()
        except (APIError, ContainerUpdateError) as error:
            if replacement is not None:
                replacement.remove(force=True)
            old.rename(original_name)
            old.start()
            raise ContainerUpdateError(
                "Update failed and the previous container was restored"
            ) from error
        return {
            "container": original_name,
            "image": release.image_reference,
            "status": "running",
        }

    def _managed_container(self):
        containers = self.client.containers.list(
            all=True, filters={"label": f"{MANAGED_LABEL}=true"}
        )
        if len(containers) != 1:
            raise ContainerUpdateError(
                "Exactly one managed quantum OS container is required"
            )
        return containers[0]

    @staticmethod
    def _wait_healthy(container, timeout: int = 90) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            container.reload()
            state = container.attrs["State"]
            health = state.get("Health", {}).get("Status")
            if health == "healthy":
                return
            if state.get("Status") in {"dead", "exited"} or health == "unhealthy":
                break
            time.sleep(2)
        raise ContainerUpdateError("Replacement container did not become healthy")
