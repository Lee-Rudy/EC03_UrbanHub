from __future__ import annotations

from pydantic import BaseModel, Field


class LoginDTO(BaseModel):
    """DTO d'entrée: on accepte uniquement email et password."""

    email: str = Field(..., examples=["user@urbanhub.tn"])
    password: str = Field(..., examples=["Password1!"])

