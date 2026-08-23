from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_ai_install_rejects_cross_site_request():
    response = client.post(
        "/api/ai/install",
        auth=("admin", "validation-password-long"),
        headers={
            "Origin": "https://attacker.example",
            "Host": "localhost:9090",
            "Sec-Fetch-Site": "cross-site",
        },
    )
    assert response.status_code == 403


def test_updater_rejects_invalid_credentials():
    response = client.get(
        "/api/ai/status", auth=("admin", "incorrect-password")
    )
    assert response.status_code == 401
