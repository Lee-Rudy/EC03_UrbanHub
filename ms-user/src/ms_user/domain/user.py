from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func

from src.core.database import Base
from src.ms_user.domain.role import Role


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    auth_user_id = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    role = Column(Enum(Role, name="user_role"), nullable=False)
    name = Column(String(120), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
