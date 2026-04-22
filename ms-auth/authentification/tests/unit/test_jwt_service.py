from __future__ import annotations

from authentification.security.jwt_service import JWTService


def test_create_and_decode_token_contains_claims() -> None:
    jwt_service = JWTService()
    token, expires_at = jwt_service.create_access_token(
        subject="123",
        email="user@urbanhub.tn",
        role="USER",
    )

    assert token
    assert expires_at is not None

    decoded = jwt_service.decode_token(token)
    assert decoded["sub"] == "123"
    assert decoded["email"] == "user@urbanhub.tn"
    assert decoded["role"] == "USER"
    assert "exp" in decoded

