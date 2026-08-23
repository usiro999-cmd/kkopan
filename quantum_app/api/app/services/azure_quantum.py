from functools import lru_cache
import re

from qdk.azure import Workspace
from qdk.azure.qiskit import AzureQuantumProvider
from qiskit import QuantumCircuit

from app.config import Settings, get_settings


class AzureQuantumConfigurationError(RuntimeError):
    pass


RESOURCE_ID_PATTERN = re.compile(
    r"^/subscriptions/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
    r"[0-9a-f]{4}-[0-9a-f]{12}/resourceGroups/[A-Za-z0-9._()\-]+/"
    r"providers/Microsoft\.Quantum/Workspaces/[A-Za-z0-9\-]+$",
    re.IGNORECASE,
)


def valid_resource_id(resource_id: str) -> bool:
    return bool(RESOURCE_ID_PATTERN.fullmatch(resource_id.strip()))


class AzureQuantumGateway:
    def __init__(self, settings: Settings):
        self.settings = settings
        if settings.azure_quantum_connection_string:
            self.workspace = Workspace.from_connection_string(
                settings.azure_quantum_connection_string
            )
        elif valid_resource_id(settings.azure_quantum_resource_id):
            self.workspace = Workspace(
                resource_id=settings.azure_quantum_resource_id
            )
        elif settings.azure_quantum_resource_id:
            raise AzureQuantumConfigurationError(
                "AZURE_QUANTUM_RESOURCE_ID must be the complete Azure resource ID."
            )
        else:
            raise AzureQuantumConfigurationError(
                "Azure Quantum is not configured. Set a workspace resource ID "
                "or connection string."
            )
        self.provider = AzureQuantumProvider(self.workspace)

    def list_targets(self) -> list[dict[str, str | None]]:
        targets = []
        for backend in self.provider.backends():
            description = getattr(backend, "description", None)
            targets.append({"name": backend.name, "description": description})
        return sorted(targets, key=lambda target: str(target["name"]))

    def submit_bell(self, target: str, shots: int):
        circuit = QuantumCircuit(2, 2)
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.measure([0, 1], [0, 1])
        backend = self.provider.get_backend(target)
        return backend.run(circuit, shots=shots)

    def get_job(self, job_id: str):
        return self.provider.get_job(job_id)


def quantum_is_configured(settings: Settings) -> bool:
    return bool(
        valid_resource_id(settings.azure_quantum_resource_id)
        or settings.azure_quantum_connection_string
    )


@lru_cache(maxsize=1)
def get_quantum_gateway() -> AzureQuantumGateway:
    return AzureQuantumGateway(get_settings())
