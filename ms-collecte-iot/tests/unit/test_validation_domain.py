from __future__ import annotations

"""
Tests unitaires pour validation_domain.py.

On teste les règles métier de validation :
  - Timestamp trop vieux
  - Confiance insuffisante
  - Valeurs hors limites
  - Détermination du statut capteur
"""

import time

import pytest

from app.domains.sensor_entity import RadarSensorEntity
from app.domains.validation_domain import (
    MIN_CONFIDENCE,
    determine_sensor_status,
    validate_sensor_entity,
)


def _make_valid_radar(**overrides) -> RadarSensorEntity:
    """
    Fonction helper : crée une entité Radar valide.
    Les overrides permettent de surcharger un champ spécifique pour tester un cas précis.

    Exemple :
        entity = _make_valid_radar(vehicle_count=-1)  # Test valeur négative
    """
    now_ms = int(time.time() * 1000)
    defaults = {
        "sensor_id": "radar_junction_001",
        "mac_address": "00:1A:2B:3C:4D:5E",
        "zone_id": "int_001",
        "sensor_type": "radar",
        "timestamp": now_ms,         # Timestamp actuel = valide
        "vehicle_count": 50,
        "occupancy_percent": 45.0,
        "detection_confidence": 0.95,
        "lane_number": 1,
        "direction": "north_to_south",
        "car": 30,
        "truck": 10,
        "motorcycle": 10,
        "avg_speed_kmh": 40.0,
    }
    defaults.update(overrides)
    return RadarSensorEntity(**defaults)


class TestValidateSensorEntity:
    """Tests des règles de validation métier."""

    def test_valid_entity_passes(self) -> None:
        """Une entité avec des données valides doit passer la validation."""
        entity = _make_valid_radar()
        is_valid, errors = validate_sensor_entity(entity)
        assert is_valid is True
        assert errors == []

    def test_rejects_old_timestamp(self) -> None:
        """Un timestamp vieux de 10 minutes doit être rejeté."""
        old_timestamp = int(time.time() * 1000) - (10 * 60 * 1000)  # il y a 10 min
        entity = _make_valid_radar(timestamp=old_timestamp)
        is_valid, errors = validate_sensor_entity(entity)
        assert is_valid is False
        assert "timestamp_too_old" in errors

    def test_rejects_future_timestamp(self) -> None:
        """Un timestamp dans le futur lointain doit être rejeté."""
        future_timestamp = int(time.time() * 1000) + (5 * 60 * 1000)  # dans 5 min
        entity = _make_valid_radar(timestamp=future_timestamp)
        is_valid, errors = validate_sensor_entity(entity)
        assert is_valid is False
        assert "timestamp_in_future" in errors

    def test_rejects_negative_vehicle_count(self) -> None:
        """Un nombre de véhicules négatif n'est pas physiquement possible."""
        entity = _make_valid_radar(vehicle_count=-1)
        is_valid, errors = validate_sensor_entity(entity)
        assert is_valid is False
        assert "vehicle_count_out_of_range" in errors

    def test_rejects_occupancy_over_100(self) -> None:
        """Un taux d'occupation > 100% est impossible."""
        entity = _make_valid_radar(occupancy_percent=150.0)
        is_valid, errors = validate_sensor_entity(entity)
        assert is_valid is False
        assert "occupancy_out_of_range" in errors

    def test_rejects_low_confidence(self) -> None:
        """Un capteur avec confiance < 0.5 doit être rejeté."""
        entity = _make_valid_radar(detection_confidence=0.3)
        is_valid, errors = validate_sensor_entity(entity)
        assert is_valid is False
        assert "confidence_too_low" in errors

    @pytest.mark.parametrize("confidence", [MIN_CONFIDENCE, 0.7, 0.95, 1.0])
    def test_accepts_valid_confidence(self, confidence: float) -> None:
        """Les confiances >= MIN_CONFIDENCE (0.5) doivent être acceptées."""
        entity = _make_valid_radar(detection_confidence=confidence)
        _, errors = validate_sensor_entity(entity)
        assert "confidence_too_low" not in errors

    def test_accepts_none_confidence(self) -> None:
        """Si le capteur ne fournit pas de confiance, c'est acceptable."""
        entity = _make_valid_radar(detection_confidence=None)
        _, errors = validate_sensor_entity(entity)
        assert "confidence_too_low" not in errors


class TestDetermineSensorStatus:
    """Tests de la détermination du statut capteur."""

    def test_valid_data_gives_ok_status(self) -> None:
        """Un capteur avec bonnes données doit avoir le statut 'ok'."""
        entity = _make_valid_radar(detection_confidence=0.95)
        status = determine_sensor_status(entity)
        assert status == "ok"

    def test_low_confidence_gives_alert_status(self) -> None:
        """Un capteur avec confiance entre 0.5 et 0.7 doit être 'en_alerte'."""
        entity = _make_valid_radar(detection_confidence=0.6)
        status = determine_sensor_status(entity)
        assert status == "en_alerte"

    def test_old_timestamp_gives_offline_status(self) -> None:
        """Un capteur sans données depuis 3 minutes doit être 'hors_ligne'."""
        old_ts = int(time.time() * 1000) - (3 * 60 * 1000)  # il y a 3 min
        entity = _make_valid_radar(timestamp=old_ts, detection_confidence=0.95)
        status = determine_sensor_status(entity)
        assert status == "hors_ligne"
