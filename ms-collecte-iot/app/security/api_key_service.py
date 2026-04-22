from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from fastapi import Header, HTTPException

from app.config import settings

logger = logging.getLogger(__name__)


def _load_api_keys() -> dict[str, dict]:
    """
    Charge le fichier JSON contenant les clés API des capteurs au démarrage.

    Le fichier api_keys.json ressemble à :
    [
      {
        "api_key": "key_radar_001_abc123",
        "mac_address": "00:1A:2B:3C:4D:5E",
        "sensor_id": "radar_junction_001",
        "sensor_type": "radar",
        "zone_id": "int_001",
        "enabled": true,
        "expires_at": "2025-12-31T23:59:59Z"
      }
    ]

    On transforme la liste en dictionnaire pour pouvoir retrouver
    les infos d'un capteur en O(1) à partir de sa clé API.
    """
    try:
        with open(settings.API_KEYS_CONFIG_PATH, "r") as f:
            keys_list = json.load(f)
        # Transforme la liste en dict : { "clé_api" → { infos du capteur } }
        return {entry["api_key"]: entry for entry in keys_list}
    except FileNotFoundError:
        logger.warning(
            "Fichier api_keys.json introuvable : %s", settings.API_KEYS_CONFIG_PATH
        )
        return {}
    except json.JSONDecodeError as e:
        logger.error("Erreur de lecture api_keys.json : %s", e)
        return {}


# Registre chargé une seule fois au démarrage de l'application
# (pas besoin de relire le fichier à chaque requête HTTP)
_SENSOR_REGISTRY: dict[str, dict] = _load_api_keys()


def verify_api_key(x_api_key: str = Header(...)) -> dict:
    """
    Dépendance FastAPI qui vérifie la clé API dans l'en-tête X-API-Key.

    FastAPI appellera automatiquement cette fonction pour chaque endpoint
    qui a `sensor_info: dict = Depends(verify_api_key)` dans sa signature.

    Retourne le dictionnaire d'infos du capteur si la clé est valide.
    Lève une HTTPException 401 (Non autorisé) si la clé est invalide.
    """
    # Cherche la clé dans le registre
    sensor_info = _SENSOR_REGISTRY.get(x_api_key)

    if not sensor_info:
        # On ne précise pas "clé introuvable" pour ne pas aider un attaquant
        logger.warning("Tentative d'accès avec une clé API invalide")
        raise HTTPException(status_code=401, detail="Clé API invalide ou manquante")

    # Vérifie que le capteur est actif
    if not sensor_info.get("enabled", False):
        logger.warning("Capteur désactivé : %s", sensor_info.get("sensor_id"))
        raise HTTPException(status_code=401, detail="Capteur désactivé")

    # Vérifie que la clé n'est pas expirée
    expires_at_str = sensor_info.get("expires_at")
    if expires_at_str:
        # fromisoformat parse la date ISO 8601 (ex: "2025-12-31T23:59:59Z")
        # Le 'Z' signifie UTC → on doit le remplacer par '+00:00' pour Python
        expires_at = datetime.fromisoformat(expires_at_str.replace("Z", "+00:00"))
        if datetime.now(tz=timezone.utc) > expires_at:
            logger.warning("Clé API expirée pour : %s", sensor_info.get("sensor_id"))
            raise HTTPException(status_code=401, detail="Clé API expirée")

    return sensor_info


def reload_api_keys() -> None:
    """
    Recharge le registre depuis le fichier JSON.
    Utile pour ajouter de nouveaux capteurs sans redémarrer le service.
    """
    global _SENSOR_REGISTRY
    _SENSOR_REGISTRY = _load_api_keys()
    logger.info("Registre des clés API rechargé : %d capteurs", len(_SENSOR_REGISTRY))
