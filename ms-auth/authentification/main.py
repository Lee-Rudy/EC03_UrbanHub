from __future__ import annotations

from fastapi import FastAPI

from authentification.controllers.auth_controller import router as auth_router
from authentification.repositories.database import Base, engine

# Création des tables à l'init (adapté pour un microservice simple).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Auth Service API",
    version="0.1.0",
    description="Service d'authentification: vérification login + génération JWT.",
)

app.include_router(auth_router)


@app.get("/", tags=["system"])
def root():
    return {"status": "ms-auth"}


@app.get("/health", tags=["system"])
def health():
    return {"status": "healthy"}