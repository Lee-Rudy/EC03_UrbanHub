from __future__ import annotations

# BaseModel de Pydantic : valide automatiquement les types et les valeurs
# Field permet d'ajouter des contraintes (min, max) et des exemples
from pydantic import BaseModel, Field


class RadarInputDTO(BaseModel):
    """
    DTO (Data Transfer Object) pour les capteurs Radar Doppler.
    Pydantic vérifie automatiquement que le JSON reçu respecte ce schéma.
    Si un champ manque ou a le mauvais type, Pydantic renvoie une erreur 422.
    """

    # Horodatage Unix en millisecondes (ex: 1713033000500 = 14 avril 2024 12:30)
    timestamp: int = Field(..., examples=[1713033000500])

    # Identifiant unique du capteur radar
    sensor_id: str = Field(..., examples=["radar_junction_001"])

    # Identifiant du carrefour où se trouve le capteur (= zone_id dans le output)
    intersection_id: str = Field(..., examples=["int_001"])

    # Numéro de la voie surveillée par ce capteur (1, 2, 3...)
    lane_number: int = Field(..., ge=1, examples=[2])

    # Direction du flux mesuré
    direction: str = Field(..., examples=["north_to_south"])

    # Nombre total de véhicules détectés pendant la période
    vehicle_count: int = Field(..., ge=0, le=10000, examples=[142])

    # Détail par type de véhicule
    car: int = Field(..., ge=0, examples=[100])
    truck: int = Field(..., ge=0, examples=[25])
    motorcycle: int = Field(..., ge=0, examples=[17])

    # Vitesse moyenne en km/h
    avg_speed_kmh: float = Field(..., ge=0.0, le=200.0, examples=[23.5])

    # Taux d'occupation de la voie en % (0-100)
    occupancy_percent: float = Field(..., ge=0.0, le=100.0, examples=[78.2])

    # Niveau de confiance du capteur (0 = pas fiable, 1 = très fiable)
    detection_confidence: float = Field(..., ge=0.0, le=1.0, examples=[0.95])
