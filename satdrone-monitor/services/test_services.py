from pathlib import Path
import sys

from fastapi.testclient import TestClient
import pytest

SERVICE_ROOT = Path(__file__).parent


@pytest.mark.parametrize(
    ("directory", "service_name"),
    [
        ("imagery", "Imagery Service"),
        ("inference", "Inference Service"),
        ("mission", "Mission Service"),
        ("drone", "Drone Service"),
        ("stream", "Stream Service"),
    ],
)
def test_service_liveness(directory: str, service_name: str) -> None:
    sys.path.insert(0, str(SERVICE_ROOT / directory))
    try:
        from app.main import app

        with TestClient(app) as client:
            response = client.get("/health/live")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "service": service_name}
    finally:
        sys.path.pop(0)
        for module_name in [name for name in sys.modules if name == "app" or name.startswith("app.")]:
            del sys.modules[module_name]

