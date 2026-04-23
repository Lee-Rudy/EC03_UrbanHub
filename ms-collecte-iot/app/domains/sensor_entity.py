from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class BaseSensorEntity:
    """
    Classe de base pour toutes les entités capteur.
    Un dataclass est une classe Python où les attributs sont déclarés simplement,
    sans avoir à écrire __init__ manuellement.

    Cette entité représente les données d'un capteur APRÈS validation et AVANT
    normalisation. C'est l'objet métier central de ce microservice.
    """

    # Identifiants (viennent du registre des capteurs, pas du JSON envoyé)
    sensor_id: str          # Ex : "radar_junction_001"
    mac_address: str        # Ex : "00:1A:2B:3C:4D:5E"
    zone_id: str            # Ex : "int_001" (= intersection_id du JSON)
    sensor_type: str        # Ex : "radar", "smartcamera", "inductiveloop"

    # Données communes à tous les capteurs
    timestamp: int          # Unix en millisecondes
    vehicle_count: int      # Nombre de véhicules comptés
    occupancy_percent: float  # Taux d'occupation en % (0-100)

    # Confiance peut être None si le capteur ne la fournit pas
    detection_confidence: Optional[float] = None


@dataclass
class RadarSensorEntity(BaseSensorEntity):
    """Entité spécifique aux capteurs Radar Doppler."""

    lane_number: int = 0
    direction: str = ""
    car: int = 0
    truck: int = 0
    motorcycle: int = 0
    avg_speed_kmh: float = 0.0


@dataclass
class SmartCameraSensorEntity(BaseSensorEntity):
    """Entité spécifique aux capteurs Smart Camera."""

    vehicle_avg_speed_kmh: float = 0.0
    traffic_flow_severity: str = "normal"
    anomaly_detected: bool = False
    anomaly_type: Optional[str] = None


@dataclass
class InductiveLoopSensorEntity(BaseSensorEntity):
    """
    Entité spécifique aux capteurs à boucle inductive.
    Note : les boucles inductives ne mesurent PAS la vitesse,
    donc avg_speed_kmh sera 0 par défaut.
    """

    lane_id: str = ""
    detection_reliability: float = 100.0
    measurement_interval: int = 30
