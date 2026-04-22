from __future__ import annotations

from datetime import datetime, timezone


def unix_ms_to_iso8601(timestamp_ms: int) -> str:
    """
    Convertit un timestamp Unix en millisecondes vers le format ISO 8601 UTC.

    Exemple :
      1713033000500 → "2024-04-14T12:30:00.500000+00:00"

    Le format ISO 8601 est le standard international pour les dates/heures.
    MS Analyse Trafic l'attend dans cet exact format.
    """
    # fromtimestamp(ts/1000) convertit les ms en secondes avant de créer la date
    dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
    return dt.isoformat()


def occupancy_percent_to_ratio(occupancy_percent: float) -> float:
    """
    Convertit un taux d'occupation en % (0-100) vers un ratio décimal (0-1).

    Exemple : 78.2% → 0.782

    MS Analyse Trafic attend le taux_occupation entre 0 et 1.
    On arrondit à 4 décimales pour éviter les flottants imprécis (ex: 0.7820000001).
    """
    return round(occupancy_percent / 100.0, 4)


def generate_event_id(timestamp_ms: int, zone_id: str) -> str:
    """
    Génère un identifiant unique pour chaque événement Kafka.

    Format : evt_{date}_{heure}_{zone}
    Exemple : "evt_20240414_123000_int001"

    L'event_id doit être unique pour permettre la déduplication côté consommateur.
    """
    dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
    # strftime formate la date : %Y=année, %m=mois, %d=jour, %H=heure, %M=minutes, %S=secondes
    date_str = dt.strftime("%Y%m%d")
    time_str = dt.strftime("%H%M%S")
    # On enlève les tirets et underscores du zone_id pour un ID plus propre
    clean_zone = zone_id.replace("-", "").replace("_", "")
    return f"evt_{date_str}_{time_str}_{clean_zone}"
