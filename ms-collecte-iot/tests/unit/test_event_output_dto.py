from __future__ import annotations

"""
Tests unitaires pour app/dtos/event_output_dto.py.

On vérifie que les DTOs de sortie (EventDetailsDTO et EventOutputDTO)
sont correctement instanciables avec des données valides.

Ces DTOs représentent le format des événements publiés dans Kafka
et consommés par MS Analyse Trafic.
"""

from app.dtos.event_output_dto import EventDetailsDTO, EventOutputDTO


class TestEventDetailsDTO:
    """Tests du sous-objet 'details' dans l'événement normalisé."""

    def test_instantiate_with_valid_data(self) -> None:
        """EventDetailsDTO doit s'instancier correctement avec des données valides."""
        details = EventDetailsDTO(
            nombre_vehicule=50,
            vitesse_moyenne_kmh=45.0,
            taux_occupation=0.5,     # Décimal 0-1, pas un pourcentage
        )

        assert details.nombre_vehicule == 50
        assert details.vitesse_moyenne_kmh == 45.0
        assert details.taux_occupation == 0.5

    def test_zero_values_are_valid(self) -> None:
        """Des valeurs à zéro (route vide) doivent être acceptées."""
        details = EventDetailsDTO(
            nombre_vehicule=0,
            vitesse_moyenne_kmh=0.0,
            taux_occupation=0.0,
        )

        assert details.nombre_vehicule == 0


class TestEventOutputDTO:
    """Tests du DTO complet de l'événement normalisé publié sur Kafka."""

    def test_instantiate_with_valid_data(self) -> None:
        """EventOutputDTO doit s'instancier avec tous ses champs requis."""
        dto = EventOutputDTO(
            event_id="evt_20240414_123000_int001",
            capteur_id="radar_junction_001",
            date_heure="2024-04-14T12:30:00.500Z",
            zone_id="int_001",
            details=EventDetailsDTO(
                nombre_vehicule=100,
                vitesse_moyenne_kmh=30.0,
                taux_occupation=0.75,
            ),
            statut_capteur="ok",
        )

        assert dto.event_id == "evt_20240414_123000_int001"
        assert dto.capteur_id == "radar_junction_001"
        assert dto.zone_id == "int_001"
        assert dto.statut_capteur == "ok"
        assert dto.details.nombre_vehicule == 100

    def test_all_sensor_statuses_are_valid(self) -> None:
        """Les 4 statuts capteur possibles doivent être acceptés sans erreur."""
        statuses = ["ok", "en_alerte", "hors_ligne", "en_panne"]

        for status in statuses:
            dto = EventOutputDTO(
                event_id=f"evt_001_{status}",
                capteur_id="radar_001",
                date_heure="2024-04-14T12:30:00.500Z",
                zone_id="int_001",
                details=EventDetailsDTO(
                    nombre_vehicule=10,
                    vitesse_moyenne_kmh=20.0,
                    taux_occupation=0.3,
                ),
                statut_capteur=status,
            )
            assert dto.statut_capteur == status
