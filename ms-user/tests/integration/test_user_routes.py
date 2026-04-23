from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_create_user_route():
    payload = {
        "auth_user_id": "auth123",
        "email": "test@mail.com",
        "name": "John",
        "role": "USER"
    }

    response = client.post("/users/", json=payload)

    assert response.status_code == 200
    assert response.json()["email"] == "test@mail.com"


def test_get_users_route():
    response = client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)