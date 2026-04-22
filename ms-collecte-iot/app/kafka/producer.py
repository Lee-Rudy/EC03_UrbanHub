from __future__ import annotations

import json
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class KafkaEventProducer:
    """
    Producteur Kafka : publie les événements normalisés dans le topic Kafka.

    Le producteur Kafka fonctionne comme un "émetteur de messages" :
      - Notre microservice = le producteur (celui qui envoie)
      - Kafka = le bus de messages (le facteur)
      - MS Analyse Trafic = le consommateur (celui qui reçoit)

    On utilise un pattern de connexion lazy (paresseuse) :
    le producteur n'est créé qu'à la première utilisation, pas au démarrage.
    Cela évite les erreurs de démarrage si Kafka n'est pas encore prêt.
    """

    def __init__(self) -> None:
        # _producer est None tant qu'on n'a pas appelé connect()
        self._producer = None

    def connect(self) -> None:
        """
        Crée la connexion au broker Kafka.
        Appelé une fois au démarrage de l'application (dans main.py).
        """
        try:
            # Import ici pour éviter une erreur au chargement si kafka-python n'est pas installé
            from kafka import KafkaProducer

            self._producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BROKERS,
                # value_serializer convertit le dict Python en bytes JSON pour Kafka
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                # key_serializer convertit la clé de partitionnement en bytes
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                # acks='all' : attend la confirmation de TOUS les réplicas avant d'acquitter
                # Plus lent mais garantit qu'aucun message n'est perdu
                acks="all",
                retries=3,
                # Délai maximum d'attente avant d'envoyer un batch (en ms)
                linger_ms=10,
            )
            logger.info("Kafka connecté sur : %s", settings.KAFKA_BROKERS)

        except Exception as e:
            logger.error("Impossible de se connecter à Kafka : %s", e)
            self._producer = None

    def publish(self, event: dict) -> bool:
        """
        Publie un événement normalisé dans le topic Kafka.

        La clé de partitionnement est le zone_id : cela garantit que tous les
        événements du même carrefour arrivent dans la même partition Kafka,
        dans l'ordre chronologique. MS Analyse Trafic peut ainsi traiter
        chaque carrefour de manière ordonnée.

        Retourne True si l'envoi a réussi, False sinon.
        """
        if self._producer is None:
            logger.error("Kafka non connecté, événement perdu : %s", event.get("event_id"))
            return False

        try:
            zone_id = event.get("zone_id", "unknown")

            # send() est non-bloquant : il met l'événement dans un buffer interne
            self._producer.send(
                topic=settings.KAFKA_TOPIC_OUTPUT,
                key=zone_id,     # Partition par zone pour garantir l'ordre
                value=event,
            )

            # flush() attend que tous les messages du buffer soient confirmés par Kafka
            self._producer.flush(timeout=5)

            logger.info(
                "Événement publié → Kafka | event_id=%s zone_id=%s",
                event.get("event_id"),
                zone_id,
            )
            return True

        except Exception as e:
            logger.error(
                "Erreur Kafka lors de la publication : %s | event_id=%s",
                e,
                event.get("event_id"),
            )
            return False

    def close(self) -> None:
        """Ferme proprement la connexion Kafka. Appelé à l'arrêt de l'application."""
        if self._producer:
            self._producer.close()
            logger.info("Kafka producteur fermé")


# Instance unique du producteur, partagée par tout le code de l'application
# On l'instancie ici mais on connecte dans main.py (lifespan)
kafka_producer = KafkaEventProducer()
