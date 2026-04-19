from __future__ import annotations

import re
from typing import Optional

"""
Validation métier des données de login.

- Email: normalisation (trim + lower) et validation basique.
- Password: au moins 6 caractères, avec majuscule, minuscule, chiffre, spécial.
"""


class Login:
    PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{6,}$")

    def __init__(self, email: str, password: str, id: Optional[int] = None):
        self._id = id
        self._email: str | None = None
        self._password: str | None = None

        self.set_email(email)
        self.set_password(password)

    def get_id(self) -> Optional[int]:
        return self._id

    def get_email(self) -> str:
        if self._email is None:
            raise ValueError("L'email n'est pas initialisé.")
        return self._email

    def get_password(self) -> str:
        if self._password is None:
            raise ValueError("Le mot de passe n'est pas initialisé.")
        return self._password

    def set_email(self, email: str) -> None:
        email = self._normalize_email(email)
        self._validate_email(email)
        self._email = email

    def set_password(self, password: str) -> None:
        password = self._normalize_password(password)
        self._validate_password(password)
        self._password = password

    def _normalize_email(self, email: str) -> str:
        if not isinstance(email, str):
            raise ValueError("L'email doit être une chaîne de caractères.")
        return email.strip().lower()

    def _normalize_password(self, password: str) -> str:
        if not isinstance(password, str):
            raise ValueError("Le mot de passe doit être une chaîne de caractères.")
        return password.strip()

    def _validate_email(self, email: str) -> None:
        if not email:
            raise ValueError("L'adresse email ne doit pas être vide.")
        if "@" not in email or "." not in email:
            raise ValueError("L'adresse email est invalide.")

    def _validate_password(self, password: str) -> None:
        if not password:
            raise ValueError("Le mot de passe ne doit pas être vide.")
        if not self.PASSWORD_REGEX.match(password):
            raise ValueError(
                "Le mot de passe doit contenir au moins 6 caractères, "
                "avec majuscule, minuscule, chiffre et caractère spécial."
            )

