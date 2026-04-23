from __future__ import annotations

import bcrypt


class BcryptPasswordHasher:
    """Service de hachage/validation des mots de passe (bcrypt).

    - `hash_password` retourne une chaîne (hash) à stocker en base.
    - `verify_password` vérifie un mot de passe en clair contre le hash stocké.
    """

    def hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )

