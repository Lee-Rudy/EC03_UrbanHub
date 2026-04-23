from fastapi import FastAPI
from src.core.database import Base, engine
from src.ms_user.domain.user import User
from src.ms_user.domain.log import Log
from src.ms_user.endpoints.user_routes import router as user_router

app = FastAPI(title="User Management Portal")
app.include_router(user_router)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"status": "User Management Okay"}