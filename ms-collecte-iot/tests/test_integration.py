from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint_status_code():
    response = client.get("/health")
    assert response.status_code == 200


def test_health_endpoint_response_body():
    response = client.get("/health")
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "ms-collecte-iot"
