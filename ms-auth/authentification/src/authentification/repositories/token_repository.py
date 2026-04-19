from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from authentification.repositories.models import AuthLogModel, AuthTokenModel


class TokenRepository:
    """Persistance des tokens générés et des logs d'authentification."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def save_access_token(
        self,
        *,
        user_id: str,
        access_token: str,
        expires_at: datetime,
        refresh_token: str | None = None,
    ) -> AuthTokenModel:
        token = AuthTokenModel(
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
        )
        self._db.add(token)
        self._db.commit()
        self._db.refresh(token)
        return token

    def log_action(self, *, user_id: str, action: str) -> AuthLogModel:
        log = AuthLogModel(user_id=user_id, action=action)
        self._db.add(log)
        self._db.commit()
        self._db.refresh(log)
        return log

