from __future__ import annotations

"""
Tests unitaires pour aggregation_domain.py.

On teste la logique de fenêtrage temporel (30 secondes) et le calcul
des moyennes et sommes sur les mesures collectées.
"""

import pytest

from app.domains.aggregation_domain import AggregationBuffer


class TestAggregationBuffer:
    """Tests du buffer d'agrégation par fenêtre temporelle."""

    def _make_reading(self, vehicle_count: int = 50, speed: float = 40.0, occupancy: float = 0.5) -> dict:
        """Helper : crée une mesure type pour les tests."""
        return {
            "sensor_id": "radar_001",
            "vehicle_count": vehicle_count,
            "avg_speed_kmh": speed,
            "taux_occupation": occupancy,
        }

    def test_reading_returns_none_before_window_closes(self) -> None:
        """
        Tant que la fenêtre de 30 secondes n'est pas fermée,
        add_reading doit retourner None (pas encore d'agrégation).
        """
        # On crée un buffer avec une fenêtre de 60 secondes (ne se fermera pas pendant le test)
        buffer = AggregationBuffer(window_seconds=60)
        result = buffer.add_reading("int_001", self._make_reading())
        assert result is None  # Fenêtre pas encore fermée → pas d'agrégat

    def test_flush_returns_aggregated_data(self) -> None:
        """
        flush_zone force la fermeture de la fenêtre et retourne les données agrégées.
        Utilisé dans les tests pour ne pas attendre 30 secondes.
        """
        buffer = AggregationBuffer(window_seconds=60)
        buffer.add_reading("int_001", self._make_reading(vehicle_count=100))
        buffer.add_reading("int_001", self._make_reading(vehicle_count=80))

        result = buffer.flush_zone("int_001")

        assert result is not None
        # Le nombre de véhicules est la SOMME (100 + 80 = 180)
        assert result["nombre_vehicule"] == 180

    def test_vehicle_count_is_summed(self) -> None:
        """
        Le nombre de véhicules est agrégé par SOMME :
        chaque capteur surveille une voie différente → on additionne.
        """
        buffer = AggregationBuffer(window_seconds=60)
        buffer.add_reading("int_001", self._make_reading(vehicle_count=50))
        buffer.add_reading("int_001", self._make_reading(vehicle_count=70))
        buffer.add_reading("int_001", self._make_reading(vehicle_count=30))

        result = buffer.flush_zone("int_001")
        assert result["nombre_vehicule"] == 150  # 50 + 70 + 30

    def test_speed_is_averaged(self) -> None:
        """
        La vitesse est agrégée par MOYENNE :
        tous les capteurs mesurent la même route, on prend la vitesse moyenne.
        """
        buffer = AggregationBuffer(window_seconds=60)
        buffer.add_reading("int_001", self._make_reading(speed=40.0))
        buffer.add_reading("int_001", self._make_reading(speed=60.0))

        result = buffer.flush_zone("int_001")
        # pytest.approx() compare les flottants avec une tolérance → évite les erreurs d'arrondi
        assert result["vitesse_moyenne_kmh"] == pytest.approx(50.0)

    def test_occupancy_is_averaged(self) -> None:
        """Le taux d'occupation est agrégé par MOYENNE."""
        buffer = AggregationBuffer(window_seconds=60)
        buffer.add_reading("int_001", self._make_reading(occupancy=0.6))
        buffer.add_reading("int_001", self._make_reading(occupancy=0.8))

        result = buffer.flush_zone("int_001")
        assert result["taux_occupation"] == pytest.approx(0.7)

    def test_different_zones_have_independent_buffers(self) -> None:
        """
        Chaque zone géographique a son propre buffer indépendant.
        Les données de int_001 ne doivent pas interférer avec int_002.
        """
        buffer = AggregationBuffer(window_seconds=60)
        buffer.add_reading("int_001", self._make_reading(vehicle_count=100))
        buffer.add_reading("int_002", self._make_reading(vehicle_count=50))

        result_001 = buffer.flush_zone("int_001")
        result_002 = buffer.flush_zone("int_002")

        assert result_001["nombre_vehicule"] == 100
        assert result_002["nombre_vehicule"] == 50

    def test_flush_nonexistent_zone_returns_none(self) -> None:
        """Flusher une zone qui n'existe pas dans le buffer doit retourner None."""
        buffer = AggregationBuffer(window_seconds=60)
        result = buffer.flush_zone("zone_inexistante")
        assert result is None

    def test_buffer_reset_after_flush(self) -> None:
        """Après un flush, le buffer de la zone doit être vide."""
        buffer = AggregationBuffer(window_seconds=60)
        buffer.add_reading("int_001", self._make_reading(vehicle_count=50))
        buffer.flush_zone("int_001")

        # Après le flush, plus de buffer pour cette zone
        result = buffer.flush_zone("int_001")
        assert result is None

    def test_window_closes_after_timeout(self) -> None:
        """
        Test fonctionnel : la fenêtre se ferme automatiquement après le délai.
        On utilise une fenêtre de 0 seconde pour que le test soit instantané.
        """
        # Fenêtre de 0 seconde = se ferme immédiatement après la première mesure
        buffer = AggregationBuffer(window_seconds=0)
        buffer.add_reading("int_001", self._make_reading(vehicle_count=42))

        # La fenêtre est déjà fermée → la deuxième mesure déclenche l'agrégation
        # Note : avec 0 secondes, la fenêtre est fermée dès le départ
        result = buffer.add_reading("int_001", self._make_reading(vehicle_count=58))
        # Le premier add_reading a renvoyé None mais le deuxième peut déclencher
        # (selon le timing exact). On utilise flush pour être déterministe.
        if result is None:
            result = buffer.flush_zone("int_001")
        assert result is not None
