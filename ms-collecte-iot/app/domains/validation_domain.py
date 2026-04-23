from __future__ import annotations

import time

from app.domains.sensor_entity import BaseSensorEntity

# Seuils de validation — définis comme constantes pour faciliter les tests et la config
MAX_TIMESTAMP_AGE_MS = 5 * 60 * 1000    # 5 minutes en millisecondes
MAX_VEHICLE_COUNT = 10_000               # Au-delà, c'est probablement une erreur capteur
MAX_SPEED_KMH = 200.0                    # Vitesse physiquement impossible à dépasser
MIN_CONFIDENCE = 0.5                     # En-dessous : donnée trop peu fiable
ALERT_CONFIDENCE_THRESHOLD = 0.7        # En-dessous : capteur passe en "en_alerte"


def validate_sensor_entity(entity: BaseSensorEntity) -> tuple[bool, list[str]]:
    """
    Valide une entité capteur selon les règles métier UrbanHub.

    Retourne un tuple :
      - bool : True si les données sont valides, False sinon
      - list[str] : liste des codes d'erreur (vide si tout est OK)

    Les codes d'erreur permettent de logger précisément pourquoi une mesure est rejetée.
    """
    errors: list[str] = []

    # Règle 1 : le timestamp ne doit pas être trop vieux
    # On compare le timestamp du capteur avec l'heure actuelle
    now_ms = int(time.time() * 1000)  # Heure actuelle en millisecondes
    age_ms = now_ms - entity.timestamp
    if age_ms > MAX_TIMESTAMP_AGE_MS:
        errors.append("timestamp_too_old")

    # Règle 2 : le timestamp ne peut pas être dans le futur
    if entity.timestamp > now_ms + 60_000:  # Tolérance d'1 minute pour décalage d'horloge
        errors.append("timestamp_in_future")

    # Règle 3 : le nombre de véhicules doit être raisonnable
    if entity.vehicle_count < 0 or entity.vehicle_count > MAX_VEHICLE_COUNT:
        errors.append("vehicle_count_out_of_range")

    # Règle 4 : le taux d'occupation doit être entre 0 et 100%
    if entity.occupancy_percent < 0.0 or entity.occupancy_percent > 100.0:
        errors.append("occupancy_out_of_range")

    # Règle 5 : niveau de confiance minimum requis
    if entity.detection_confidence is not None:
        if entity.detection_confidence < MIN_CONFIDENCE:
            errors.append("confidence_too_low")

    return len(errors) == 0, errors


def determine_sensor_status(entity: BaseSensorEntity) -> str:
    """
    Détermine le statut du capteur à inclure dans l'événement Kafka.

    Statuts possibles :
      - "ok"         : tout est normal
      - "en_alerte"  : confiance entre 0.5 et 0.7 (données utilisables mais dégradées)
      - "hors_ligne" : timestamp trop vieux (capteur n'envoie plus)
      - "en_panne"   : données manifestement incorrectes
    """
    now_ms = int(time.time() * 1000)

    # Si pas de données depuis 2 minutes → hors ligne
    if (now_ms - entity.timestamp) > 2 * 60 * 1000:
        return "hors_ligne"

    # Si plusieurs valeurs invalides → en panne
    is_valid, errors = validate_sensor_entity(entity)
    if not is_valid and len(errors) > 1:
        return "en_panne"

    # Si la confiance est faible mais acceptable → en alerte
    if (
        entity.detection_confidence is not None
        and entity.detection_confidence < ALERT_CONFIDENCE_THRESHOLD
    ):
        return "en_alerte"

    return "ok"
