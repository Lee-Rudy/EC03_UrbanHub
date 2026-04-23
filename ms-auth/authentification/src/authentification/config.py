from __future__ import annotations

import os


class Settings:
    """Configuration applicative.

    Les variables d'environnement attendues (avec valeurs par défaut) :
    - DATABASE_URL: URL SQLAlchemy (ex: postgresql+psycopg://user:pass@host:5432/db)
    - JWT_SECRET_KEY: secret de signature des tokens
    - JWT_ALGORITHM: algorithme (par défaut HS256)
    - JWT_ACCESS_TOKEN_EXPIRE_MINUTES: durée de validité (minutes)
    """

    def __init__(self) -> None:
        self.database_url = os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://postgres:postgres@localhost:5432/db_auth",
        )

        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_access_token_expire_minutes = int(
            os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
        )


settings = Settings()

