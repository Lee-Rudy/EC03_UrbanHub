from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.domains.aggregation_domain import aggregation_buffer
from app.domains.mapper import SensorMapper
from app.domains.normalization_domain import occupancy_percent_to_ratio
from app.domains.validation_domain import validate_sensor_entity
from app.dtos.inductiveloop_input_dto import InductiveLoopInputDTO
from app.dtos.radar_input_dto import RadarInputDTO
from app.dtos.smartcamera_input_dto import SmartCameraInputDTO
from app.kafka.producer import kafka_producer
from app.repositories.sensor_repository import SensorRepository
from app.security.api_key_service import verify_api_key

logger = logging.getLogger(__name__)

# APIRouter est comme un "sous-routeur" FastAPI.
# On le monte sur l'application principale dans main.py avec un prefix "/api/v1/sensors".
router = APIRouter(prefix="/api/v1/sensors", tags=["sensors"])

# Une seule instance du repository, réutilisée pour tous les appels
sensor_repo = SensorRepository()


def _process_sensor_event(entity, sensor_info: dict) -> dict:
    """
    Pipeline de traitement commun à tous les types de capteurs.

    Étapes :
      1. Valider les données du capteur (règles métier)
      2. Construire l'événement Kafka à partir de l'entité
      3. Ajouter au buffer d'agrégation
      4. Si la fenêtre est fermée → publier sur Kafka et sauvegarder en MongoDB

    Retourne le dict de réponse HTTP.
    """
    # Étape 1 — Validation métier
    is_valid, errors = validate_sensor_entity(entity)
    if not is_valid:
        logger.warning(
            "Données invalides rejetées | sensor=%s erreurs=%s",
            entity.sensor_id,
            errors,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Données capteur invalides : {errors}",
        )

    # Étape 2 — Conversion vers le format de stockage dans le buffer
    # On prépare un dict allégé pour le buffer (pas l'événement Kafka complet)
    reading = {
        "sensor_id": entity.sensor_id,
        "vehicle_count": entity.vehicle_count,
        "taux_occupation": occupancy_percent_to_ratio(entity.occupancy_percent),
    }

    # Ajoute la vitesse si le capteur en fournit une
    if hasattr(entity, "avg_speed_kmh"):
        reading["avg_speed_kmh"] = entity.avg_speed_kmh
    elif hasattr(entity, "vehicle_avg_speed_kmh"):
        reading["avg_speed_kmh"] = entity.vehicle_avg_speed_kmh
    else:
        reading["avg_speed_kmh"] = 0.0

    # Étape 3 — Ajout au buffer d'agrégation
    # add_reading retourne None si la fenêtre de 30 secondes n'est pas encore fermée
    aggregated = aggregation_buffer.add_reading(entity.zone_id, reading)

    if aggregated:
        # La fenêtre de 30 secondes est fermée → on construit l'événement Kafka final
        kafka_event = SensorMapper.entity_to_kafka_event(entity)

        # On remplace les détails par les données agrégées (moyenne de la fenêtre)
        kafka_event["details"]["nombre_vehicule"] = aggregated["nombre_vehicule"]
        kafka_event["details"]["vitesse_moyenne_kmh"] = aggregated["vitesse_moyenne_kmh"]
        kafka_event["details"]["taux_occupation"] = aggregated["taux_occupation"]

        # Étape 4a — Publier sur Kafka
        kafka_producer.publish(kafka_event)

        # Étape 4b — Sauvegarder en MongoDB (pour audit / RGPD)
        sensor_repo.save_event(kafka_event)

        logger.info(
            "Événement agrégé publié | zone=%s véhicules=%s",
            entity.zone_id,
            aggregated["nombre_vehicule"],
        )

    return {
        "status": "received",
        "sensor_id": entity.sensor_id,
        "zone_id": entity.zone_id,
        "message": "Données reçues et en cours d'agrégation",
    }


@router.post("/radar", status_code=status.HTTP_201_CREATED)
def receive_radar_data(
    data: RadarInputDTO,
    sensor_info: dict = Depends(verify_api_key),  # FastAPI vérifie la clé API automatiquement
) -> dict:
    """
    Reçoit les données d'un capteur Radar Doppler.

    Headers requis :
      X-API-Key: {clé_api_du_capteur}

    Retourne 201 si les données sont acceptées.
    Retourne 400 si les données sont invalides.
    Retourne 401 si la clé API est invalide ou absente.
    """
    logger.info(
        "Données Radar reçues | sensor=%s zone=%s",
        sensor_info["sensor_id"],
        data.intersection_id,
    )

    # Convertit le DTO HTTP en entité métier
    entity = SensorMapper.radar_dto_to_entity(data, sensor_info)
    return _process_sensor_event(entity, sensor_info)


@router.post("/smartcamera", status_code=status.HTTP_201_CREATED)
def receive_smartcamera_data(
    data: SmartCameraInputDTO,
    sensor_info: dict = Depends(verify_api_key),
) -> dict:
    """Reçoit les données d'un capteur Smart Camera."""
    logger.info(
        "Données SmartCamera reçues | sensor=%s zone=%s",
        sensor_info["sensor_id"],
        data.intersection_id,
    )

    entity = SensorMapper.smartcamera_dto_to_entity(data, sensor_info)
    return _process_sensor_event(entity, sensor_info)


@router.post("/inductiveloop", status_code=status.HTTP_201_CREATED)
def receive_inductiveloop_data(
    data: InductiveLoopInputDTO,
    sensor_info: dict = Depends(verify_api_key),
) -> dict:
    """Reçoit les données d'une boucle inductive."""
    logger.info(
        "Données Boucle Inductive reçues | sensor=%s zone=%s",
        sensor_info["sensor_id"],
        data.intersection_id,
    )

    entity = SensorMapper.inductiveloop_dto_to_entity(data, sensor_info)
    return _process_sensor_event(entity, sensor_info)
