from __future__ import annotations

"""
Tests unitaires pour app/database/mongo_client.py.

On teste le client MongoDB EN ISOLATION en mockant pymongo.MongoClient.
Aucune vraie base de données n'est utilisée ici.

Cas couverts :
  - Connexion réussie → _client et _database initialisés
  - Connexion échouée (serveur injoignable) → reste None
  - get_database() → retourne _database
  - close() → ferme proprement la connexion
"""

from unittest.mock import MagicMock, patch

from app.database.mongo_client import MongoDBClient


class TestConnect:
    """Tests de la méthode connect() du client MongoDB."""

    def test_connect_success(self) -> None:
        """connect() doit initialiser _client et _database si MongoDB répond."""
        client = MongoDBClient()
        mock_mongo = MagicMock()  # MagicMock gère automatiquement .admin.command() et __getitem__

        with patch("pymongo.MongoClient", return_value=mock_mongo):
            client.connect()

        assert client._client is mock_mongo
        assert client._database is not None

    def test_connect_failure_sets_none(self) -> None:
        """Si MongoDB est injoignable, _client et _database restent None."""
        client = MongoDBClient()

        with patch("pymongo.MongoClient", side_effect=Exception("Connection refused")):
            client.connect()

        assert client._client is None
        assert client._database is None


class TestGetDatabase:
    """Tests de la méthode get_database()."""

    def test_returns_database_when_connected(self) -> None:
        """get_database() doit retourner _database si la connexion est active."""
        client = MongoDBClient()
        mock_db = MagicMock()
        client._database = mock_db

        result = client.get_database()

        assert result is mock_db

    def test_returns_none_when_not_connected(self) -> None:
        """get_database() doit retourner None si connect() n'a pas été appelé."""
        client = MongoDBClient()
        # _database est None par défaut

        result = client.get_database()

        assert result is None


class TestClose:
    """Tests de la méthode close() du client MongoDB."""

    def test_close_with_client(self) -> None:
        """close() doit appeler .close() sur le client PyMongo."""
        client = MongoDBClient()
        mock_mongo = MagicMock()
        client._client = mock_mongo

        client.close()

        mock_mongo.close.assert_called_once()

    def test_close_without_client_does_not_raise(self) -> None:
        """close() sans connexion ne doit pas lever d'exception."""
        client = MongoDBClient()
        # _client est None → ne doit pas planter
        client.close()
