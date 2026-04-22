from __future__ import annotations

"""
Tests unitaires pour normalization_domain.py.

Les tests unitaires vérifient une SEULE fonction à la fois, sans dépendances externes.
Ici on teste les conversions de données : timestamp, taux d'occupation, event_id.
"""

import pytest

from app.domains.normalization_domain import (
    generate_event_id,
    occupancy_percent_to_ratio,
    unix_ms_to_iso8601,
)


class TestUnixToIso8601:
    """Tests de la conversion timestamp Unix → ISO 8601."""

    def test_converts_known_timestamp(self) -> None:
        """Vérifie qu'un timestamp connu produit la bonne date ISO."""
        # 1713033000500 ms = 2024-04-13 18:30:00.5 UTC
        result = unix_ms_to_iso8601(1713033000500)
        # On vérifie que la date et l'heure sont présentes (format ISO 8601)
        assert "2024-04-13" in result
        assert "+00:00" in result  # Doit être en UTC

    def test_result_is_string(self) -> None:
        """Le résultat doit être une chaîne de caractères."""
        result = unix_ms_to_iso8601(1713033000500)
        assert isinstance(result, str)

    def test_zero_timestamp(self) -> None:
        """Timestamp 0 = 1er janvier 1970 (epoch Unix)."""
        result = unix_ms_to_iso8601(0)
        assert "1970-01-01" in result


class TestOccupancyToRatio:
    """Tests de la conversion taux d'occupation % → ratio décimal."""

    def test_100_percent_becomes_1(self) -> None:
        """100% doit donner exactement 1.0."""
        assert occupancy_percent_to_ratio(100.0) == 1.0

    def test_0_percent_becomes_0(self) -> None:
        """0% doit donner exactement 0.0."""
        assert occupancy_percent_to_ratio(0.0) == 0.0

    def test_78_percent_converts_correctly(self) -> None:
        """78.2% doit donner 0.782 (arrondi à 4 décimales)."""
        result = occupancy_percent_to_ratio(78.2)
        assert result == pytest.approx(0.782, abs=0.0001)

    def test_result_is_between_0_and_1(self) -> None:
        """Le ratio doit toujours être entre 0 et 1."""
        for percent in [0, 25.5, 50, 75.3, 100]:
            ratio = occupancy_percent_to_ratio(percent)
            assert 0.0 <= ratio <= 1.0, f"Ratio hors limites pour {percent}%"


class TestGenerateEventId:
    """Tests de la génération d'identifiants d'événements."""

    def test_contains_zone_id(self) -> None:
        """L'event_id doit contenir une version nettoyée du zone_id."""
        event_id = generate_event_id(1713033000500, "int_001")
        # "int_001" → "int001" (underscore supprimé)
        assert "int001" in event_id

    def test_starts_with_evt(self) -> None:
        """L'event_id doit commencer par 'evt_'."""
        event_id = generate_event_id(1713033000500, "int_001")
        assert event_id.startswith("evt_")

    def test_different_timestamps_give_different_ids(self) -> None:
        """Deux timestamps différents doivent produire deux event_ids différents."""
        id1 = generate_event_id(1713033000000, "int_001")
        id2 = generate_event_id(1713033060000, "int_001")  # 60 secondes plus tard
        assert id1 != id2

    def test_different_zones_give_different_ids(self) -> None:
        """Même timestamp, zones différentes → event_ids différents."""
        id1 = generate_event_id(1713033000500, "int_001")
        id2 = generate_event_id(1713033000500, "int_002")
        assert id1 != id2
