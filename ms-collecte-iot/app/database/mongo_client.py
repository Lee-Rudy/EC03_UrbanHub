from __future__ import annotations

import logging

from app.config import settings

logger = logging.getLogger(__name__)


class MongoDBClient:
    """
    Client MongoDB pour ce microservice.

    MongoDB est utilisé comme buffer de persistance pour les fenêtres d'agrégation.
    Si le service redémarre pendant une fenêtre de 30 secondes, les données
    en cours d'agrégation ne sont pas perdues (elles sont sauvegardées en base).

    Pattern utilisé : connexion lazy (créée à la première utilisation).
    """

    def __init__(self) -> None:
        self._client = None      # Client PyMongo
        self._database = None    # Base de données MongoDB

    def connect(self) -> None:
        """
        Ouvre la connexion à MongoDB.
        Appelé au démarrage de l'application dans main.py.
        """
        try:
            from pymongo import MongoClient

            self._client = MongoClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=5000,  # Timeout de 5 secondes pour la connexion
            )

            # ismaster est un ping léger pour vérifier que MongoDB répond
            self._client.admin.command("ismaster")

            # Sélectionne (ou crée) la base de données
            self._database = self._client[settings.MONGODB_DB_NAME]

            logger.info("MongoDB connecté : base '%s'", settings.MONGODB_DB_NAME)

        except Exception as e:
            logger.error("Impossible de se connecter à MongoDB : %s", e)
            self._client = None
            self._database = None

    def get_database(self):
        """Retourne l'objet base de données MongoDB."""
        return self._database

    def close(self) -> None:
        """Ferme proprement la connexion MongoDB."""
        if self._client:
            self._client.close()
            logger.info("MongoDB connexion fermée")


# Instance unique partagée dans toute l'application
mongo_client = MongoDBClient()
