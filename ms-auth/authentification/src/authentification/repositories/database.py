from __future__ import annotations

"""Configuration SQLAlchemy (engine, session, base déclarative)."""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from authentification.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dépendance FastAPI pour obtenir une session DB.

    Usage: `db: Session = Depends(get_db)`
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

