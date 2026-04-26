from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_admin_can_get_users():
    response = client.get("/users/", headers={"X-Role": "ADMIN"})
    assert response.status_code == 200

def test_user_cannot_get_users():
    response = client.get("/users/", headers={"X-Role": "USER"})
    assert response.status_code == 403
