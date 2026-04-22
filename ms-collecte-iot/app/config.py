from __future__ import annotations

# os.environ permet de lire les variables d'environnement du système
import os

# load_dotenv() lit le fichier .env et charge les variables dans os.environ
from dotenv import load_dotenv

# On charge le fichier .env dès l'import de ce module
load_dotenv()


class Settings:
    """
    Centralise toute la configuration de l'application.
    Chaque attribut correspond à une variable d'environnement.
    Si la variable n'existe pas, on utilise une valeur par défaut.
    """

    # ── Application ───────────────────────────────────────────
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8002"))
    APP_ENV: str = os.getenv("APP_ENV", "development")

    # ── Kafka ─────────────────────────────────────────────────
    # KAFKA_BROKERS peut contenir plusieurs adresses séparées par des virgules
    # Ex : "kafka1:9092,kafka2:9092"
    KAFKA_BROKERS: list[str] = os.getenv("KAFKA_BROKERS", "localhost:9092").split(",")
    KAFKA_TOPIC_OUTPUT: str = os.getenv(
        "KAFKA_TOPIC_OUTPUT", "traffic_events_normalized"
    )

    # ── MongoDB ───────────────────────────────────────────────
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "urbanhub_collecte")

    # ── Authentification capteurs ─────────────────────────────
    # Fichier JSON qui contient la liste des clés API des capteurs IoT
    API_KEYS_CONFIG_PATH: str = os.getenv(
        "API_KEYS_CONFIG_PATH", "./config/api_keys.json"
    )

    # ── RGPD ──────────────────────────────────────────────────
    DATA_RETENTION_DAYS: int = int(os.getenv("DATA_RETENTION_DAYS", "30"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


# Instance unique des settings, importée partout dans l'application
settings = Settings()
