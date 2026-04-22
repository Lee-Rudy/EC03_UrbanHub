from __future__ import annotations

"""
Tests unitaires pour app/kafka/producer.py.

On teste le producteur Kafka EN ISOLATION : on ne se connecte jamais à un vrai
broker Kafka. On utilise unittest.mock.patch pour remplacer la vraie
bibliothèque kafka-python par un objet simulé (mock).

Pourquoi mocker Kafka ici ?
  - Les tests unitaires doivent être rapides et sans infrastructure externe
  - Kafka n'est pas disponible en CI par défaut
  - On veut tester la LOGIQUE du producer, pas Kafka lui-même
"""

from unittest.mock import MagicMock, patch

from app.kafka.producer import KafkaEventProducer


class TestConnect:
    """Tests de la méthode connect() du producteur Kafka."""

    def test_connect_success(self) -> None:
        """connect() doit créer le producer Kafka et stocker l'instance."""
        producer = KafkaEventProducer()
        mock_instance = MagicMock()

        # On patche KafkaProducer dans le module kafka (importé dynamiquement dans connect())
        with patch("kafka.KafkaProducer", return_value=mock_instance):
            producer.connect()

        # Après une connexion réussie, _producer doit pointer sur l'instance mockée
        assert producer._producer is mock_instance

    def test_connect_failure_sets_producer_to_none(self) -> None:
        """Si la connexion Kafka échoue (broker indisponible), _producer reste None."""
        producer = KafkaEventProducer()

        with patch("kafka.KafkaProducer", side_effect=Exception("Broker unavailable")):
            producer.connect()

        # Aucune exception ne doit remonter, mais _producer doit rester None
        assert producer._producer is None


class TestPublish:
    """Tests de la méthode publish() du producteur Kafka."""

    def test_publish_when_not_connected_returns_false(self) -> None:
        """publish() sans connexion Kafka préalable doit retourner False."""
        producer = KafkaEventProducer()
        # _producer est None par défaut (connexion non initiée)

        result = producer.publish({"event_id": "evt_001", "zone_id": "int_001"})

        assert result is False

    def test_publish_success_returns_true(self) -> None:
        """publish() avec un producer actif doit retourner True."""
        producer = KafkaEventProducer()
        producer._producer = MagicMock()  # Simule un producer déjà connecté

        event = {"event_id": "evt_001", "zone_id": "int_001"}
        result = producer.publish(event)

        assert result is True
        producer._producer.send.assert_called_once()
        producer._producer.flush.assert_called_once_with(timeout=5)

    def test_publish_exception_returns_false(self) -> None:
        """Si send() lève une exception, publish() doit retourner False sans planter."""
        producer = KafkaEventProducer()
        producer._producer = MagicMock()
        producer._producer.send.side_effect = Exception("Kafka error")

        result = producer.publish({"event_id": "evt_002", "zone_id": "int_002"})

        assert result is False

    def test_publish_uses_zone_id_as_partition_key(self) -> None:
        """publish() doit envoyer l'événement avec zone_id comme clé de partition."""
        producer = KafkaEventProducer()
        producer._producer = MagicMock()

        event = {"event_id": "evt_003", "zone_id": "int_005"}
        producer.publish(event)

        call_kwargs = producer._producer.send.call_args.kwargs
        assert call_kwargs["key"] == "int_005"


class TestClose:
    """Tests de la méthode close() du producteur Kafka."""

    def test_close_with_producer(self) -> None:
        """close() doit appeler .close() sur le producer Kafka actif."""
        producer = KafkaEventProducer()
        mock_instance = MagicMock()
        producer._producer = mock_instance

        producer.close()

        mock_instance.close.assert_called_once()

    def test_close_without_producer_does_not_raise(self) -> None:
        """close() sans connexion ne doit pas lever d'exception."""
        producer = KafkaEventProducer()
        # _producer est None → ne doit pas planter
        producer.close()