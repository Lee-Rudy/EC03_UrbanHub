from __future__ import annotations

"""
Tests unitaires pour app/domains/mapper.py.

On teste les 4 méthodes du SensorMapper :
  - radar_dto_to_entity()        : DTO Radar → entité métier
  - smartcamera_dto_to_entity()  : DTO Smart Camera → entité métier
  - inductiveloop_dto_to_entity(): DTO Boucle Inductive → entité métier
  - entity_to_kafka_event()      : entité → dict Kafka (3 branches: Radar, SmartCam, InductiveLoop)
"""

import time

import pytest

from app.domains.mapper import SensorMapper
from app.domains.sensor_entity import (
    InductiveLoopSensorEntity,
    RadarSensorEntity,
    SmartCameraSensorEntity,
)
from app.dtos.inductiveloop_input_dto import InductiveLoopInputDTO
from app.dtos.radar_input_dto import RadarInputDTO
from app.dtos.smartcamera_input_dto import SmartCameraInputDTO

# Infos du registre capteur : simule ce qui est lu depuis api_keys.json
_SENSOR_INFO = {
    "sensor_id": "radar_junction_001",
    "mac_address": "00:1A:2B:3C:4D:5E",
}

_NOW_MS = int(time.time() * 1000)


# ── DTO → Entity ───────────────────────────────────────────────────────────────

class TestRadarDtoToEntity:
    """Tests de la conversion DTO Radar → RadarSensorEntity."""

    def test_converts_all_fields_correctly(self) -> None:
        """Tous les champs du DTO doivent être transférés vers l'entité."""
        dto = RadarInputDTO(
            timestamp=_NOW_MS,
            sensor_id="radar_junction_001",
            intersection_id="int_001",
            lane_number=2,
            direction="north_to_south",
            vehicle_count=100,
            car=70,
            truck=20,
            motorcycle=10,
            avg_speed_kmh=45.0,
            occupancy_percent=60.0,
            detection_confidence=0.92,
        )

        entity = SensorMapper.radar_dto_to_entity(dto, _SENSOR_INFO)

        assert isinstance(entity, RadarSensorEntity)
        assert entity.sensor_id == "radar_junction_001"
        assert entity.mac_address == "00:1A:2B:3C:4D:5E"
        assert entity.zone_id == "int_001"        # intersection_id → zone_id
        assert entity.sensor_type == "radar"
        assert entity.avg_speed_kmh == 45.0
        assert entity.vehicle_count == 100


class TestSmartCameraDtoToEntity:
    """Tests de la conversion DTO Smart Camera → SmartCameraSensorEntity."""

    def test_converts_all_fields_correctly(self) -> None:
        dto = SmartCameraInputDTO(
            timestamp=_NOW_MS,
            sensor_id="smartcam_junction_001",
            intersection_id="int_001",
            vehicle_count=80,
            vehicle_avg_speed_kmh=55.0,
            occupancy_percent=40.0,
            traffic_flow_severity="normal",
            anomaly_detected=False,
            anomaly_type=None,
            detection_confidence=0.88,
        )

        entity = SensorMapper.smartcamera_dto_to_entity(dto, _SENSOR_INFO)

        assert isinstance(entity, SmartCameraSensorEntity)
        assert entity.vehicle_avg_speed_kmh == 55.0
        assert entity.anomaly_detected is False
        assert entity.anomaly_type is None
        assert entity.sensor_type == "smartcamera"


class TestInductiveLoopDtoToEntity:
    """Tests de la conversion DTO Boucle Inductive → InductiveLoopSensorEntity."""

    def test_converts_all_fields_correctly(self) -> None:
        dto = InductiveLoopInputDTO(
            timestamp=_NOW_MS,
            sensor_id="loop_junction_001_lane_1",
            intersection_id="int_001",
            lane_id="lane_1",
            vehicle_count=60,
            occupancy_percent=35.0,
            detection_reliability=90.0,
            measurement_interval=30,
        )

        entity = SensorMapper.inductiveloop_dto_to_entity(dto, _SENSOR_INFO)

        assert isinstance(entity, InductiveLoopSensorEntity)
        assert entity.lane_id == "lane_1"
        assert entity.measurement_interval == 30

    def test_converts_detection_reliability_to_confidence(self) -> None:
        """detection_reliability (0-100) doit être converti en detection_confidence (0-1)."""
        dto = InductiveLoopInputDTO(
            timestamp=_NOW_MS,
            sensor_id="loop_junction_001_lane_1",
            intersection_id="int_001",
            lane_id="lane_1",
            vehicle_count=60,
            occupancy_percent=35.0,
            detection_reliability=90.0,   # 90% → 0.90
            measurement_interval=30,
        )

        entity = SensorMapper.inductiveloop_dto_to_entity(dto, _SENSOR_INFO)

        # La division par 100 convertit le % en valeur décimale
        assert entity.detection_confidence == pytest.approx(0.90)


# ── Entity → Kafka event ───────────────────────────────────────────────────────

class TestEntityToKafkaEvent:
    """
    Tests de la conversion entité → événement Kafka.

    C'est ici qu'on couvre les 3 branches du if/elif/else dans entity_to_kafka_event :
      - isinstance(entity, RadarSensorEntity)      → speed = avg_speed_kmh
      - isinstance(entity, SmartCameraSensorEntity) → speed = vehicle_avg_speed_kmh
      - else (InductiveLoop)                        → speed = 0.0
    """

    def _make_base_fields(self) -> dict:
        """Champs communs requis par BaseSensorEntity."""
        return {
            "sensor_id": "sensor_001",
            "mac_address": "00:AA:BB:CC:DD:EE",
            "zone_id": "int_001",
            "timestamp": _NOW_MS,
            "vehicle_count": 50,
            "occupancy_percent": 50.0,
            "detection_confidence": 0.90,
        }

    def test_radar_uses_avg_speed_kmh(self) -> None:
        """Pour un Radar, la vitesse dans l'événement Kafka = avg_speed_kmh."""
        entity = RadarSensorEntity(
            **self._make_base_fields(),
            sensor_type="radar",
            avg_speed_kmh=42.0,
        )

        event = SensorMapper.entity_to_kafka_event(entity)

        assert event["details"]["vitesse_moyenne_kmh"] == 42.0
        assert event["zone_id"] == "int_001"
        assert "event_id" in event
        assert "date_heure" in event

    def test_smartcamera_uses_vehicle_avg_speed_kmh(self) -> None:
        """Pour une SmartCamera, la vitesse dans l'événement Kafka = vehicle_avg_speed_kmh."""
        entity = SmartCameraSensorEntity(
            **self._make_base_fields(),
            sensor_type="smartcamera",
            vehicle_avg_speed_kmh=35.0,
        )

        event = SensorMapper.entity_to_kafka_event(entity)

        assert event["details"]["vitesse_moyenne_kmh"] == 35.0

    def test_inductiveloop_speed_is_zero(self) -> None:
        """Pour une boucle inductive (pas de capteur de vitesse), vitesse = 0.0."""
        entity = InductiveLoopSensorEntity(
            **self._make_base_fields(),
            sensor_type="inductiveloop",
        )

        event = SensorMapper.entity_to_kafka_event(entity)

        # C'est la branche else du if/elif/else dans entity_to_kafka_event
        assert event["details"]["vitesse_moyenne_kmh"] == 0.0

    def test_occupancy_is_converted_to_ratio(self) -> None:
        """occupancy_percent 50% doit être converti en taux_occupation 0.5."""
        entity = RadarSensorEntity(
            **self._make_base_fields(),
            sensor_type="radar",
        )

        event = SensorMapper.entity_to_kafka_event(entity)

        # occupancy_percent_to_ratio(50.0) = 0.5
        assert event["details"]["taux_occupation"] == pytest.approx(0.5)

    def test_output_contains_required_kafka_fields(self) -> None:
        """L'événement Kafka doit contenir tous les champs requis par MS Analyse Trafic."""
        entity = RadarSensorEntity(
            **self._make_base_fields(),
            sensor_type="radar",
        )

        event = SensorMapper.entity_to_kafka_event(entity)

        required_fields = {"event_id", "capteur_id", "date_heure", "zone_id", "details", "statut_capteur"}
        assert required_fields.issubset(event.keys())
        assert "nombre_vehicule" in event["details"]