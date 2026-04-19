from __future__ import annotations

from sqlalchemy.orm import Session

from authentification.repositories.models import UserModel


class UserRepository:
    """Accès DB aux utilisateurs."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_email(self, email: str) -> UserModel | None:
        return (
            self._db.query(UserModel)
            .filter(UserModel.email == email)
            .one_or_none()
        )

