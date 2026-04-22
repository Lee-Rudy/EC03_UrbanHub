from __future__ import annotations

from pydantic import BaseModel, Field


class EventDetailsDTO(BaseModel):
    """Sous-objet 'details' dans l'événement normalisé publié sur Kafka."""

    nombre_vehicule: int
    vitesse_moyenne_kmh: float
    # taux_occupation est en DECIMAL 0-1 (pas en %, contrairement aux inputs)
    taux_occupation: float


class EventOutputDTO(BaseModel):
    """
    Structure de l'événement normalisé publié dans le topic Kafka
    'traffic_events_normalized'. C'est le format que consomme MS Analyse Trafic.
    """

    # Identifiant unique de l'événement, généré par ce microservice
    event_id: str = Field(..., examples=["evt_20240414_123000_int001"])

    # Identifiant du capteur qui a envoyé la donnée d'origine
    capteur_id: str = Field(..., examples=["radar_junction_001"])

    # Date/heure en format ISO 8601 UTC (ex: "2024-04-14T12:30:00.500Z")
    date_heure: str = Field(..., examples=["2024-04-14T12:30:00.500Z"])

    # Zone géographique = identifiant du carrefour
    zone_id: str = Field(..., examples=["int_001"])

    details: EventDetailsDTO

    # État du capteur : ok | en_alerte | hors_ligne | en_panne
    statut_capteur: str = Field(..., examples=["ok"])
