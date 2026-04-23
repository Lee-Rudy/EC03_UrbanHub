import os

class Settings:
    APP_NAME = os.getenv("APP_NAME", "ms-user")
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/userdb"
    )

settings = Settings()
