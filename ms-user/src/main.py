from fastapi import FastAPI
from src.core.database import Base, engine

from src.ms_user.domain.user import User
from src.ms_user.domain.log import Log

app = FastAPI(title="User Management Portal")

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"status": "User Management Okay"}