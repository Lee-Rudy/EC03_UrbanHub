from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from src.core.database import Base


class Log(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False)
    action = Column(String(255), nullable=False)
    resource = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
