from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.database.mongo_client import mongo_client

logger = logging.getLogger(__name__)

# Nom des collections MongoDB utilisées par ce microservice
COLLECTION_EVENTS = "events"        # Événements normalisés publiés sur Kafka
COLLECTION_BUFFER = "agg_buffer"    # Buffer d'agrégation (crash resilience)


class SensorRepository:
    """
    Couche d'accès aux données MongoDB.

    En architecture hexagonale, le repository est la seule couche
    qui connaît la base de données. Les couches domaine et contrôleur
    ne savent pas si on utilise MongoDB, PostgreSQL ou un fichier JSON.

    Rôle de ce repository :
      - Sauvegarder les événements publiés sur Kafka (pour audit / RGPD)
      - Persister le buffer d'agrégation (pour survie aux redémarrages)
    """

    def _get_collection(self, name: str):
        """
        Retourne une collection MongoDB.
        Si MongoDB n'est pas connecté, retourne None et loggue l'erreur.
        """
        db = mongo_client.get_database()
        if db is None:
            logger.warning("MongoDB non disponible, opération ignorée")
            return None
        return db[name]

    def save_event(self, event: dict) -> bool:
        """
        Sauvegarde un événement normalisé dans MongoDB après publication Kafka.

        Pourquoi sauvegarder si l'événement est déjà dans Kafka ?
        → Kafka garde les données 7 jours. MongoDB permet de garder un historique
          plus long et de faire des requêtes SQL-like pour le reporting RGPD.

        Retourne True si sauvegardé avec succès.
        """
        collection = self._get_collection(COLLECTION_EVENTS)
        if collection is None:
            return False

        try:
            # On ajoute la date de sauvegarde pour le suivi RGPD
            document = {
                **event,
                "saved_at": datetime.now(tz=timezone.utc).isoformat(),
            }
            collection.insert_one(document)
            return True

        except Exception as e:
            logger.error("Erreur MongoDB save_event : %s", e)
            return False

    def save_buffer_snapshot(self, zone_id: str, readings: list[dict]) -> bool:
        """
        Sauvegarde le buffer d'agrégation en cours pour une zone.

        Si le service redémarre pendant une fenêtre de 30 secondes,
        on peut récupérer ce snapshot et continuer l'agrégation.
        """
        collection = self._get_collection(COLLECTION_BUFFER)
        if collection is None:
            return False

        try:
            # upsert=True : crée le document s'il n'existe pas, le remplace sinon
            collection.replace_one(
                {"zone_id": zone_id},  # filtre : cherche par zone_id
                {
                    "zone_id": zone_id,
                    "readings": readings,
                    "updated_at": datetime.now(tz=timezone.utc).isoformat(),
                },
                upsert=True,
            )
            return True

        except Exception as e:
            logger.error("Erreur MongoDB save_buffer_snapshot : %s", e)
            return False

    def delete_events_older_than_days(self, days: int) -> int:
        """
        Supprime les événements plus vieux que N jours.
        Appelé périodiquement pour respecter la politique RGPD de rétention.

        Retourne le nombre de documents supprimés.
        """
        collection = self._get_collection(COLLECTION_EVENTS)
        if collection is None:
            return 0

        try:
            from datetime import timedelta

            cutoff = datetime.now(tz=timezone.utc) - timedelta(days=days)
            # Supprime tous les documents dont saved_at est plus vieux que la date limite
            result = collection.delete_many({"saved_at": {"$lt": cutoff.isoformat()}})
            logger.info(
                "RGPD : %d événements supprimés (> %d jours)", result.deleted_count, days
            )
            return result.deleted_count

        except Exception as e:
            logger.error("Erreur MongoDB delete_events_older_than_days : %s", e)
            return 0
