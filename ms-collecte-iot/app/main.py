from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.controllers.sensor_controller import router as sensor_router
from app.database.mongo_client import mongo_client
from app.kafka.producer import kafka_producer

# Configuration du logger pour toute l'application
# %(asctime)s = heure, %(levelname)s = INFO/WARNING/ERROR, %(message)s = le message
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestionnaire de cycle de vie de l'application FastAPI.

    Le code AVANT le 'yield' s'exécute au DÉMARRAGE du serveur.
    Le code APRÈS le 'yield' s'exécute à l'ARRÊT du serveur.

    C'est ici qu'on ouvre et ferme les connexions aux services externes
    (Kafka et MongoDB), pour éviter les fuites de connexion.
    """
    # ── Démarrage ───────────────────────────────────────────────
    logger.info("Démarrage MS Collecte IoT (port %s)...", settings.APP_PORT)

    # Connexion à MongoDB
    mongo_client.connect()

    # Connexion à Kafka
    kafka_producer.connect()

    logger.info("MS Collecte IoT prêt ✓")

    # yield = point de pause : l'application tourne ici jusqu'à l'arrêt
    yield

    # ── Arrêt ────────────────────────────────────────────────────
    logger.info("Arrêt MS Collecte IoT...")
    kafka_producer.close()
    mongo_client.close()


# Création de l'application FastAPI
# lifespan = notre gestionnaire de démarrage/arrêt
app = FastAPI(
    title="MS Collecte IoT",
    description="Microservice de collecte et normalisation des données capteurs IoT — UrbanHub",
    version="0.1.0",
    lifespan=lifespan,
)

# Montage du routeur des capteurs
# Tous les endpoints /api/v1/sensors/* seront gérés par sensor_controller.py
app.include_router(sensor_router)


@app.get("/health", tags=["monitoring"])
def health_check() -> dict:
    """
    Endpoint de santé — utilisé par Docker et les load balancers pour
    savoir si le service est vivant et prêt à recevoir du trafic.
    """
    return {
        "status": "healthy",
        "service": "ms-collecte-iot",
        "version": "0.1.0",
    }
