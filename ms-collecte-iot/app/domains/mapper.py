from __future__ import annotations

from app.domains.normalization_domain import (
    generate_event_id,
    occupancy_percent_to_ratio,
    unix_ms_to_iso8601,
)
from app.domains.sensor_entity import (
    InductiveLoopSensorEntity,
    RadarSensorEntity,
    SmartCameraSensorEntity,
)
from app.domains.validation_domain import determine_sensor_status
from app.dtos.inductiveloop_input_dto import InductiveLoopInputDTO
from app.dtos.radar_input_dto import RadarInputDTO
from app.dtos.smartcamera_input_dto import SmartCameraInputDTO


class SensorMapper:
    """
    Le Mapper transforme les données entre les différentes couches de l'application.

    Flux de transformation :
      1. DTO (JSON reçu via HTTP)  →  Entity (objet métier Python)
      2. Entity  →  dict (format JSON pour Kafka)

    On sépare ces transformations du reste du code pour respecter
    le principe de responsabilité unique (chaque classe fait UNE chose).
    """

    @staticmethod
    def radar_dto_to_entity(dto: RadarInputDTO, sensor_info: dict) -> RadarSensorEntity:
        """
        Convertit un DTO Radar + les infos du registre capteur en entité métier.

        sensor_info est le dictionnaire récupéré depuis api_keys.json,
        il contient le mac_address, zone_id, etc. qui ne sont pas dans le JSON du capteur.
        """
        return RadarSensorEntity(
            sensor_id=sensor_info["sensor_id"],
            mac_address=sensor_info["mac_address"],
            zone_id=dto.intersection_id,
            sensor_type="radar",
            timestamp=dto.timestamp,
            vehicle_count=dto.vehicle_count,
            occupancy_percent=dto.occupancy_percent,
            detection_confidence=dto.detection_confidence,
            lane_number=dto.lane_number,
            direction=dto.direction,
            car=dto.car,
            truck=dto.truck,
            motorcycle=dto.motorcycle,
            avg_speed_kmh=dto.avg_speed_kmh,
        )

    @staticmethod
    def smartcamera_dto_to_entity(
        dto: SmartCameraInputDTO, sensor_info: dict
    ) -> SmartCameraSensorEntity:
        """Convertit un DTO Smart Camera en entité métier."""
        return SmartCameraSensorEntity(
            sensor_id=sensor_info["sensor_id"],
            mac_address=sensor_info["mac_address"],
            zone_id=dto.intersection_id,
            sensor_type="smartcamera",
            timestamp=dto.timestamp,
            vehicle_count=dto.vehicle_count,
            occupancy_percent=dto.occupancy_percent,
            detection_confidence=dto.detection_confidence,
            vehicle_avg_speed_kmh=dto.vehicle_avg_speed_kmh,
            traffic_flow_severity=dto.traffic_flow_severity,
            anomaly_detected=dto.anomaly_detected,
            anomaly_type=dto.anomaly_type,
        )

    @staticmethod
    def inductiveloop_dto_to_entity(
        dto: InductiveLoopInputDTO, sensor_info: dict
    ) -> InductiveLoopSensorEntity:
        """
        Convertit un DTO boucle inductive en entité métier.
        Note : les boucles n'ont pas de vitesse, avg_speed_kmh restera à 0.
        """
        return InductiveLoopSensorEntity(
            sensor_id=sensor_info["sensor_id"],
            mac_address=sensor_info["mac_address"],
            zone_id=dto.intersection_id,
            sensor_type="inductiveloop",
            timestamp=dto.timestamp,
            vehicle_count=dto.vehicle_count,
            occupancy_percent=dto.occupancy_percent,
            # Les boucles inductives donnent une "fiabilité" (0-100) pas une "confiance" (0-1)
            # On convertit en divisant par 100 pour avoir le même format que les autres capteurs
            detection_confidence=dto.detection_reliability / 100.0,
            lane_id=dto.lane_id,
            detection_reliability=dto.detection_reliability,
            measurement_interval=dto.measurement_interval,
        )

    @staticmethod
    def entity_to_kafka_event(entity: RadarSensorEntity | SmartCameraSensorEntity | InductiveLoopSensorEntity) -> dict:
        """
        Transforme une entité métier en dict prêt à être publié sur Kafka.

        Ce dict correspond au schéma de l'événement normalisé défini dans CLAUDE.md.
        C'est le format que consomme MS Analyse Trafic.
        """
        # Détermine la vitesse selon le type de capteur
        # (les boucles inductives n'ont pas de vitesse → 0.0)
        if isinstance(entity, RadarSensorEntity):
            speed = entity.avg_speed_kmh
        elif isinstance(entity, SmartCameraSensorEntity):
            speed = entity.vehicle_avg_speed_kmh
        else:
            # InductiveLoop : pas de mesure de vitesse
            speed = 0.0

        return {
            "event_id": generate_event_id(entity.timestamp, entity.zone_id),
            "capteur_id": entity.sensor_id,
            # Convertit le timestamp Unix ms → ISO 8601 UTC
            "date_heure": unix_ms_to_iso8601(entity.timestamp),
            "zone_id": entity.zone_id,
            "details": {
                "nombre_vehicule": entity.vehicle_count,
                "vitesse_moyenne_kmh": speed,
                # Convertit le % (0-100) en ratio décimal (0-1) comme attendu par Analyse Trafic
                "taux_occupation": occupancy_percent_to_ratio(entity.occupancy_percent),
            },
            # Détermine automatiquement si le capteur est ok, en alerte, etc.
            "statut_capteur": determine_sensor_status(entity),
        }
