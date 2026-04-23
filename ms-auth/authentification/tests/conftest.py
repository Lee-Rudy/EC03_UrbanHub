from __future__ import annotations

import os

"""Configuration tests.

Pytest importe les `conftest.py` avant de collecter les tests. Comme ton `main.py`
se connecte à la DB dès l'import, on doit forcer les variables d'environnement
ICI (au niveau module) pour éviter toute tentative de connexion Postgres.
"""

# Base SQLite locale pour tests (fichier dans le répertoire de travail).
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

# JWT de test.
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-with-min-32-bytes!!")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")

