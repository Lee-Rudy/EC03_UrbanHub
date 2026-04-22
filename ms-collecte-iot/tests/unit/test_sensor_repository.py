from __future__ import annotations

"""
Tests unitaires pour app/repositories/sensor_repository.py.

On teste le repository MongoDB EN ISOLATION en mockant mongo_client.
La vraie base MongoDB n'est jamais utilisée ici.

Stratégie :
  - patch("app.repositories.sensor_repository.mongo_client") remplace
    l'instance globale par un mock
  - On contrôle ce que get_database() retourne pour simuler MongoDB
    disponible / indisponible / en erreur
"""

from unittest.mock import MagicMock, patch

from app.repositories.sensor_repository import SensorRepository


def _make_repo() -> SensorRepository:
    return SensorRepository()


# ── _get_collection ────────────────────────────────────────────────────────────

class TestGetCollection:
    """Tests de la méthode interne _get_collection()."""

    def test_returns_none_when_mongo_unavailable(self) -> None:
        """Si MongoDB n'est pas connecté, _get_collection doit retourner None."""
        repo = _make_repo()

        with patch("app.repositories.sensor_repository.mongo_client") as mock_client:
            mock_client.get_database.return_value = None
            result = repo._get_collection("events")

        assert result is None

    def test_returns_collection_when_available(self) -> None:
        """Si MongoDB est disponible, _get_collection doit retourner la collection."""
        repo = _make_repo()
        mock_db = MagicMock()

        with patch("app.repositories.sensor_repository.mongo_client") as mock_client:
            mock_client.get_database.return_value = mock_db
            result = repo._get_collection("events")

        # mock_db["events"] est automatiquement un MagicMock (not None)
        assert result is not None


# ── save_event ─────────────────────────────────────────────────────────────────

class TestSaveEvent:
    """Tests de la méthode save_event()."""

    def test_returns_false_when_mongo_unavailable(self) -> None:
        """save_event doit retourner False si MongoDB n'est pas connecté."""
        repo = _make_repo()

        with patch("app.repositories.sensor_repository.mongo_client") as mock_client:
            mock_client.get_database.return_value = None
            result = repo.save_event({"event_id": "evt_001"})

        assert result is False

    def test_returns_true_on_success(self) -> None:
        """save_event doit insérer le document et retourner True."""
        repo = _make_repo()
        mock_db = MagicMock()

        with patch("app.repositories.sensor_repository.mongo_client") as mock_client:
            mock_client.get_database.return_value = mock_db
            result = repo.save_event({"event_id": "evt_001"})

        assert result is True
        mock_db.__getitem__.return_value.insert_one.assert_called_once()

    def test_returns_false_on_insert_exception(self) -> None:
        """save_event doit retourner False si insert_one lève une exception."""
        repo = _make_repo()
        mock_db = MagicMock()
        mock_db.__getitem__.return_value.insert_one.side_effect = Exception("DB error")

        with patch("app.repositories.sensor_repository.mongo_client") as mock_client:
            mock_client.get_database.return_value = mock_db
            result = repo.save_event({"event_id": "evt_001"})

        assert result is False


# ── save_buffer_snapshot ───────────────────────────────────────────────────────

class TestSaveBufferSnapshot:
    """Tests de la méthode save_buffer_snapshot()."""

    def test_returns_false_when_mongo_unavailable(self) -> None:
        """save_buffer_snapshot doit retourner False si MongoDB n'est pas connecté."""
        repo = _make_repo()

        with patch("app.repositories.sensor_repository.mongo_client") as mock_client:
            mock_client.get_database.return_value = None
            result = repo.save_buffer_snapshot("int_001", [])

        assert result is False

    def test_returns_true_on_success(self) -> None:
        """save_buffer_snapshot doit faire un upsert et retourner True."""
        repo = _make_repo()
        mock_db = MagicMock()

        with patch("app.repositories.sensor_repository.mongo_client") as mock_client:
            mock_client.get_database.return_value = mock_db
            result = repo.save_buffer_snapshot("int_001", [{"data": 1}])

        assert result is True
        mock_db.__getitem__.return_value.replace_one.assert_called_once()

    def test_returns_false_on_replace_exception(self) -> None:
        """save_buffer_snapshot doit retourner False si replace_one lève une exception."""
        repo = _make_repo()
        mock_db = MagicMock()
        mock_db.__getitem__.return_value.replace_one.side_effect = Exception("DB error")

        with patch("app.repositories.sensor_repository.mongo_client") as mock_client:
            mock_client.get_database.return_value = mock_db
            result = repo.save_buffer_snapshot("int_001", [])

        assert result is False


# ── delete_events_older_than_days ─────────────────────────────────────────────

class TestDeleteEventsOlderThanDays:
    """Tests de la méthode delete_events_older_than_days() (RGPD)."""

    def test_returns_zero_when_mongo_unavailable(self) -> None:
        """Si MongoDB n'est pas connecté, aucune suppression → retourne 0."""
        repo = _make_repo()

        with patch("app.repositories.sensor_repository.mongo_client") as mock_client:
            mock_client.get_database.return_value = None
            result = repo.delete_events_older_than_days(30)

        assert result == 0

    def test_returns_deleted_count_on_success(self) -> None:
        """delete_events_older_than_days doit retourner le nombre de documents supprimés."""
        repo = _make_repo()
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.deleted_count = 5
        mock_db.__getitem__.return_value.delete_many.return_value = mock_result

        with patch("app.repositories.sensor_repository.mongo_client") as mock_client:
            mock_client.get_database.return_value = mock_db
            result = repo.delete_events_older_than_days(30)

        assert result == 5

    def test_returns_zero_on_delete_exception(self) -> None:
        """delete_events_older_than_days doit retourner 0 si delete_many lève une exception."""
        repo = _make_repo()
        mock_db = MagicMock()
        mock_db.__getitem__.return_value.delete_many.side_effect = Exception("DB error")

        with patch("app.repositories.sensor_repository.mongo_client") as mock_client:
            mock_client.get_database.return_value = mock_db
            result = repo.delete_events_older_than_days(30)

        assert result == 0