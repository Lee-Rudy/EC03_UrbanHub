from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt

from authentification.config import settings


class JWTService:
    """Création et décodage des JWT (PyJWT).

    Contenu standard des claims émis:
    - sub: identifiant utilisateur (string)
    - email: email normalisé
    - role: rôle (USER, CELLULE_DECISIONNEL, OPERATEUR)
    - exp: expiration (UTC)
    """

    def create_access_token(self, *, subject: str, email: str, role: str) -> tuple[str, datetime]:
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )
        payload = {
            "sub": subject,
            "email": email,
            "role": role,
            "exp": expires_at,
        }
        token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        return token, expires_at

    def decode_token(self, token: str) -> dict:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

