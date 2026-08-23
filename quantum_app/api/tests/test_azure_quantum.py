from app.config import Settings
from app.services.azure_quantum import quantum_is_configured, valid_resource_id


def test_azure_quantum_is_not_configured_by_default():
    assert not quantum_is_configured(Settings())


def test_resource_id_configures_azure_quantum():
    settings = Settings(
        azure_quantum_resource_id=(
            "/subscriptions/00000000-0000-0000-0000-000000000000/"
            "resourceGroups/rg/providers/"
            "Microsoft.Quantum/Workspaces/workspace"
        )
    )
    assert quantum_is_configured(settings)


def test_connection_string_configures_azure_quantum():
    settings = Settings(azure_quantum_connection_string="fake-connection-string")
    assert quantum_is_configured(settings)


def test_workspace_name_alone_is_not_a_resource_id():
    assert not valid_resource_id("workspace-name")
    assert not quantum_is_configured(
        Settings(azure_quantum_resource_id="workspace-name")
    )
    assert not valid_resource_id(
        "/subscriptions/<ID>/resourceGroups/<GROUP>/providers/"
        "Microsoft.Quantum/Workspaces/<WORKSPACE>"
    )
