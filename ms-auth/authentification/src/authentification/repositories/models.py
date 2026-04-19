from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from authentification.domains.user_role import UserRole
from authentification.repositories.database import Base


class UserModel(Base):
    """Utilisateur minimal pour l'authentification.

    Note: dans ton architecture globale, la gestion des utilisateurs peut être
    externalisée dans un autre microservice. Ici on stocke seulement ce qui est
    nécessaire pour valider un login et générer un token.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AuthTokenModel(Base):
    __tablename__ = "auth_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AuthLogModel(Base):
    __tablename__ = "logs_authentification"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

