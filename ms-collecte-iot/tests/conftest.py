from __future__ import annotations

"""
conftest.py : configuration globale de pytest.

Ce fichier est automatiquement chargé par pytest AVANT tous les tests.
C'est ici qu'on configure l'environnement de test pour éviter que les tests
essaient de se connecter à de vrais services (Kafka, MongoDB).

Pourquoi forcer les variables d'environnement ici et pas dans les tests ?
→ Parce que les imports Python sont exécutés une seule fois.
  Si on importe app.config avant de définir les variables, les valeurs
  par défaut sont déjà figées. En les définissant ici (au niveau module),
  elles sont disponibles dès le premier import.
"""

import os

# ── Application ────────────────────────────────────────────────────────
os.environ.setdefault("APP_HOST", "0.0.0.0")
os.environ.setdefault("APP_PORT", "8002")
os.environ.setdefault("APP_ENV", "test")

# ── Kafka ──────────────────────────────────────────────────────────────
# On pointe vers un broker inexistant : les tests ne doivent PAS envoyer
# de vrais messages Kafka. On mockera le producer dans les tests.
os.environ.setdefault("KAFKA_BROKERS", "localhost:9999")
os.environ.setdefault("KAFKA_TOPIC_OUTPUT", "test_topic")

# ── MongoDB ────────────────────────────────────────────────────────────
os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27099")
os.environ.setdefault("MONGODB_DB_NAME", "test_db")

# ── Fichier de clés API ────────────────────────────────────────────────
# Pointe vers le vrai fichier de test dans config/
os.environ.setdefault("API_KEYS_CONFIG_PATH", "./config/api_keys.json")

# ── Logging ────────────────────────────────────────────────────────────
os.environ.setdefault("LOG_LEVEL", "WARNING")  # Silencieux pendant les tests
