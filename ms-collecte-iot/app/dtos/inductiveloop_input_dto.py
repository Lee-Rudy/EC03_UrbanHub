from __future__ import annotations

from pydantic import BaseModel, Field


class InductiveLoopInputDTO(BaseModel):
    """
    DTO pour les capteurs à boucle inductive.
    Ces capteurs sont encastrés dans la chaussée et détectent le passage des véhicules
    via un champ électromagnétique. Ils sont très fiables mais ne donnent pas de vitesse.
    """

    timestamp: int = Field(..., examples=[1713033000500])
    sensor_id: str = Field(..., examples=["loop_junction_001_lane_1"])
    intersection_id: str = Field(..., examples=["int_001"])

    # Identifiant de la voie spécifique surveillée par cette boucle
    lane_id: str = Field(..., examples=["lane_1"])

    vehicle_count: int = Field(..., ge=0, le=10000, examples=[135])
    occupancy_percent: float = Field(..., ge=0.0, le=100.0, examples=[82.3])

    # Fiabilité de la détection en % (dépend de l'état de la boucle dans la chaussée)
    detection_reliability: float = Field(..., ge=0.0, le=100.0, examples=[98.5])

    # Durée de la fenêtre de mesure en secondes (généralement 30 secondes)
    measurement_interval: int = Field(..., ge=1, examples=[30])
