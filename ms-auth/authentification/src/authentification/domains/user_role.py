from __future__ import annotations

from enum import Enum


class UserRole(str, Enum):
    """Rôles autorisés pour l'émission de tokens."""

    USER = "USER"
    CELLULE_DECISIONNEL = "CELLULE_DECISIONNEL"
    OPERATEUR = "OPERATEUR"

