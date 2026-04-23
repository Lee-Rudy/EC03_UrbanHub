from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from authentification.repositories.database import Base, SessionLocal, engine
from authentification.repositories.models import AuthLogModel, AuthTokenModel, UserModel
from authentification.security.password_hasher import BcryptPasswordHasher

import main


@pytest.fixture()
def client() -> TestClient:
    """Client FastAPI + DB SQLite initialisée pour les tests d'intégration."""
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Nettoyage entre tests (SQLite).
        db.execute(delete(AuthTokenModel))
        db.execute(delete(AuthLogModel))
        db.execute(delete(UserModel))
        db.commit()

        hasher = BcryptPasswordHasher()
        db.add_all(
            [
                UserModel(
                    email="user@urbanhub.tn",
                    password_hash=hasher.hash_password("Password1!"),
                    role="USER",
                    name="User Test",
                ),
                UserModel(
                    email="cellule@urbanhub.tn",
                    password_hash=hasher.hash_password("Password2!"),
                    role="CELLULE_DECISIONNEL",
                    name="Cellule Test",
                ),
                UserModel(
                    email="operateur@urbanhub.tn",
                    password_hash=hasher.hash_password("Password3!"),
                    role="OPERATEUR",
                    name="Operateur Test",
                ),
            ]
        )
        db.commit()
    finally:
        db.close()

    return TestClient(main.app)


@pytest.mark.parametrize(
    "email,password",
    [
        ("user@urbanhub.tn", "Password1!"),
        ("cellule@urbanhub.tn", "Password2!"),
        ("operateur@urbanhub.tn", "Password3!"),
    ],
)
def test_login_success_returns_token(client: TestClient, email: str, password: str) -> None:
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200

    data = r.json()
    assert "access_token" in data
    assert isinstance(data["access_token"], str) and len(data["access_token"]) > 10
    assert data["token_type"] == "bearer"


def test_login_invalid_password_returns_401(client: TestClient) -> None:
    r = client.post(
        "/auth/login",
        json={"email": "user@urbanhub.tn", "password": "WrongPassword1!"},
    )
    assert r.status_code == 401


def test_login_invalid_email_format_returns_422(client: TestClient) -> None:
    r = client.post("/auth/login", json={"email": "invalid", "password": "Password1!"})
    assert r.status_code == 422

