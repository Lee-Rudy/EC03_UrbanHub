from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class SmartCameraInputDTO(BaseModel):
    """
    DTO pour les capteurs Smart Camera.
    Les caméras fournissent des métadonnées de trafic (pas d'images ni de plaques).
    """

    timestamp: int = Field(..., examples=[1713033000500])
    sensor_id: str = Field(..., examples=["smartcam_junction_001"])
    intersection_id: str = Field(..., examples=["int_001"])

    vehicle_count: int = Field(..., ge=0, le=10000, examples=[148])
    vehicle_avg_speed_kmh: float = Field(..., ge=0.0, le=200.0, examples=[24.0])
    occupancy_percent: float = Field(..., ge=0.0, le=100.0, examples=[76.5])

    # Sévérité du flux : normal, slow (lent), congested (embouteillage)
    traffic_flow_severity: str = Field(..., examples=["normal"])

    # Si True, la caméra a détecté quelque chose d'anormal (accident, piéton, etc.)
    anomaly_detected: bool = Field(..., examples=[False])

    # Type d'anomalie détectée (None si anomaly_detected est False)
    anomaly_type: Optional[str] = Field(None, examples=[None])

    detection_confidence: float = Field(..., ge=0.0, le=1.0, examples=[0.92])
