from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional


# Durée d'une fenêtre d'agrégation en secondes
WINDOW_SIZE_SECONDS = 30


@dataclass
class ZoneBuffer:
    """
    Buffer de données pour une zone géographique (carrefour).

    L'agrégation consiste à collecter toutes les mesures pendant 30 secondes,
    puis à les moyenner pour produire UN seul événement Kafka par zone.

    Sans agrégation, on pourrait envoyer 3 événements séparés
    (un par type de capteur) pour le même carrefour au même moment.
    L'agrégation les fusionne en un seul événement plus représentatif.
    """

    zone_id: str
    # Heure de début de la fenêtre (timestamp Python en secondes)
    window_start: float = field(default_factory=time.time)
    # Liste des mesures collectées pendant la fenêtre
    readings: list[dict] = field(default_factory=list)


class AggregationBuffer:
    """
    Gestionnaire des fenêtres temporelles d'agrégation.

    Comment ça marche :
      1. Un capteur envoie des données → on les ajoute au buffer de sa zone
      2. Quand la fenêtre de 30 secondes est fermée → on calcule la moyenne
      3. Le résultat agrégé est retourné pour être publié sur Kafka
      4. Le buffer de la zone est réinitialisé
    """

    def __init__(self, window_seconds: int = WINDOW_SIZE_SECONDS) -> None:
        self._window_seconds = window_seconds
        # Dictionnaire : zone_id → ZoneBuffer
        # Chaque carrefour a son propre buffer indépendant
        self._buffers: dict[str, ZoneBuffer] = {}

    def add_reading(self, zone_id: str, reading: dict) -> Optional[dict]:
        """
        Ajoute une mesure au buffer de la zone.

        Retourne un dict d'agrégation si la fenêtre de 30 secondes est fermée,
        ou None si on attend encore d'autres données.

        Le dict retourné contient les données moyennées, prêtes pour Kafka.
        """
        # Crée un nouveau buffer si c'est la première mesure de cette zone
        if zone_id not in self._buffers:
            self._buffers[zone_id] = ZoneBuffer(zone_id=zone_id)

        # Ajoute la mesure au buffer
        self._buffers[zone_id].readings.append(reading)

        # Vérifie si la fenêtre de 30 secondes est terminée
        if self._is_window_closed(zone_id):
            # Calcule les moyennes sur toutes les mesures de la fenêtre
            aggregated = self._aggregate(zone_id)
            # Réinitialise le buffer pour la prochaine fenêtre
            del self._buffers[zone_id]
            return aggregated

        # La fenêtre n'est pas encore fermée → on attend d'autres données
        return None

    def _is_window_closed(self, zone_id: str) -> bool:
        """Vérifie si 30 secondes se sont écoulées depuis l'ouverture de la fenêtre."""
        buffer = self._buffers[zone_id]
        elapsed = time.time() - buffer.window_start
        return elapsed >= self._window_seconds

    def _aggregate(self, zone_id: str) -> dict:
        """
        Calcule les statistiques agrégées sur toutes les mesures de la fenêtre.

        Pour le nombre de véhicules : on fait la SOMME (pas la moyenne).
          → Si 3 capteurs détectent 50, 60, 70 véhicules = 180 véhicules au total

        Pour la vitesse et l'occupation : on fait la MOYENNE.
          → La moyenne de vitesse de tous les capteurs = vitesse représentative de la zone
        """
        readings = self._buffers[zone_id].readings

        if not readings:
            return {
                "zone_id": zone_id,
                "nombre_vehicule": 0,
                "vitesse_moyenne_kmh": 0.0,
                "taux_occupation": 0.0,
            }

        # Somme des véhicules (chaque capteur surveille une voie différente)
        total_vehicles = sum(r.get("vehicle_count", 0) for r in readings)

        # Moyenne des vitesses (certains capteurs peuvent ne pas avoir de vitesse)
        speeds = [r["avg_speed_kmh"] for r in readings if r.get("avg_speed_kmh", 0) > 0]
        avg_speed = sum(speeds) / len(speeds) if speeds else 0.0

        # Moyenne des taux d'occupation (déjà en ratio 0-1 dans les readings)
        occupancies = [r.get("taux_occupation", 0.0) for r in readings]
        avg_occupancy = sum(occupancies) / len(occupancies)

        return {
            "zone_id": zone_id,
            "nombre_vehicule": total_vehicles,
            "vitesse_moyenne_kmh": round(avg_speed, 2),
            "taux_occupation": round(avg_occupancy, 4),
        }

    def flush_zone(self, zone_id: str) -> Optional[dict]:
        """
        Force la fermeture de la fenêtre pour une zone, même avant les 30 secondes.

        Utilisé pour les tests et pour vider le buffer proprement à l'arrêt du service.
        """
        if zone_id not in self._buffers:
            return None
        aggregated = self._aggregate(zone_id)
        del self._buffers[zone_id]
        return aggregated


# Instance unique partagée par toute l'application (pattern Singleton)
# Cela garantit qu'un seul buffer existe pour chaque zone
aggregation_buffer = AggregationBuffer()
