# MS Collecte IoT

Microservice de **collecte, normalisation et agrégation** des données capteurs IoT pour le projet **UrbanHub** — reçoit les données brutes des capteurs de trafic urbain, les valide, les agrège sur des fenêtres de 30 secondes et publie les événements normalisés vers **Apache Kafka**.

![CI/CD](https://github.com/Lee-Rudy/EC03_UrbanHub/actions/workflows/ms-collecte-iot.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green)
![Coverage](https://img.shields.io/badge/Coverage-72%25-yellowgreen)
![Docker](https://img.shields.io/badge/Docker-ready-blue)

---

## Sommaire

- [Rôle dans l'architecture UrbanHub](#rôle-dans-larchitecture-urbanhub)
- [Stack technique](#stack-technique)
- [Structure du projet](#structure-du-projet)
- [Installation locale](#installation-locale)
- [Démarrage rapide](#démarrage-rapide)
- [API — Endpoints capteurs](#api--endpoints-capteurs)
- [Authentification des capteurs](#authentification-des-capteurs)
- [Formats de données](#formats-de-données)
- [Tests](#tests)
- [Docker](#docker)
- [CI/CD](#cicd)
- [Variables d'environnement](#variables-denvironnement)
- [Conformité RGPD](#conformité-rgpd)

---

## Rôle dans l'architecture UrbanHub

```
Capteurs IoT (Radar, Smart Camera, Boucles inductives)
       │
       │  POST /api/v1/sensors/{type}
       │  Header: X-API-Key
       ▼
┌─────────────────────────────────────────────────────┐
│         MS COLLECTE IoT  (port 8002)                │
│                                                     │
│  1. Authentification capteur (API Key)              │
│  2. Validation métier (plages, confiance, timestamp)│
│  3. Agrégation 30 secondes par zone                 │
│  4. Normalisation (ISO 8601, ratio 0-1)             │
└──────────────────────┬──────────────────────────────┘
                       │  Kafka topic: traffic_events_normalized
                       ▼
            MS Analyse Trafic (port 8008)
                  ├─→ indicateurTrafic
                  ├─→ scoreCongestion
                  └─→ MS Alerte (port 8005)
```

### Microservices UrbanHub — ports

| Microservice | Port |
|---|---|
| API Gateway | 8000 |
| MS Authentification | 8001 |
| **MS Collecte IoT** | **8002** |
| MS Analyse Trafic | 8008 |
| MS Alerte | 8005 |

---

## Stack technique

| Composant | Technologie | Version |
|---|---|---|
| Langage | Python | 3.11 |
| Framework API | FastAPI | 0.110 |
| Serveur ASGI | Uvicorn | 0.29 |
| Validation données | Pydantic | v2 |
| Bus de messages | Apache Kafka (KRaft) | 3.7.0 |
| Client Kafka | kafka-python | 2.0 |
| Base de données buffer | MongoDB | 7.0 |
| Client MongoDB | PyMongo | 4.6 |
| Gestion dépendances | Poetry | 1.8.2 |
| Containerisation | Docker | - |
| Tests | pytest + pytest-cov | 8.x |
| Linter | flake8 | 7.0 |

---

## Structure du projet

```
ms-collecte-iot/
├── app/
│   ├── main.py                     # Point d'entrée FastAPI (lifespan Kafka+MongoDB)
│   ├── config.py                   # Variables d'environnement centralisées
│   │
│   ├── controllers/
│   │   └── sensor_controller.py    # Endpoints POST /api/v1/sensors/*
│   │
│   ├── dtos/                       # Data Transfer Objects (schémas HTTP Pydantic)
│   │   ├── radar_input_dto.py      # 12 champs Radar Doppler
│   │   ├── smartcamera_input_dto.py # 10 champs Smart Camera
│   │   ├── inductiveloop_input_dto.py # 8 champs Boucle Inductive
│   │   └── event_output_dto.py     # 8 champs événement Kafka normalisé
│   │
│   ├── domains/                    # Logique métier pure (pas de dépendance externe)
│   │   ├── sensor_entity.py        # Entités métier (dataclasses)
│   │   ├── normalization_domain.py # Conversions (timestamp, unités)
│   │   ├── validation_domain.py    # Règles métier + statut capteur
│   │   ├── aggregation_domain.py   # Fenêtres glissantes 30s par zone
│   │   └── mapper.py               # DTO → Entity → Événement Kafka
│   │
│   ├── security/
│   │   └── api_key_service.py      # Vérification X-API-Key (FastAPI Depends)
│   │
│   ├── kafka/
│   │   └── producer.py             # Publication sur traffic_events_normalized
│   │
│   ├── database/
│   │   └── mongo_client.py         # Connexion MongoDB (lazy)
│   │
│   └── repositories/
│       └── sensor_repository.py    # Accès MongoDB (buffer + audit RGPD)
│
├── tests/
│   ├── conftest.py                 # Variables d'environnement de test
│   ├── unit/
│   │   ├── test_normalization_domain.py
│   │   ├── test_validation_domain.py
│   │   └── test_aggregation_domain.py
│   └── integration/
│       └── test_sensor_controller.py
│
├── config/
│   └── api_keys.json               # Registre des clés API capteurs
│
├── reports/                        # Rapports de tests (gitignored)
│   ├── junit.xml
│   ├── coverage.xml
│   └── htmlcov/
│
├── Dockerfile                      # Image de production
├── Dockerfile.test                 # Image de test (CI/CD)
├── docker-compose.yml              # Stack locale : Kafka + MongoDB + MS
├── pyproject.toml                  # Dépendances (Poetry)
└── .env.example                    # Modèle de configuration
```

### Architecture hexagonale

```
HTTP (controllers/)           ← Reçoit les requêtes, authentifie, parse les DTOs
        ↓
Domaine (domains/)            ← Validation, normalisation, agrégation (logique métier)
        ↓
Infrastructure (kafka/, database/, repositories/)  ← Kafka, MongoDB
```

> La couche domaine ne connaît pas Kafka ni MongoDB.
> Elle manipule uniquement des objets Python (entités, dicts).

---

## Installation locale

### Prérequis

- Python 3.11+
- [Poetry](https://python-poetry.org/docs/#installation)
- Docker + Docker Compose

### Étapes

```bash
# 1. Cloner le repo
git clone https://github.com/Lee-Rudy/EC03_UrbanHub.git
cd EC03_UrbanHub/ms-collecte-iot

# 2. Configurer l'environnement
cp .env.example .env

# 3. Installer les dépendances Python
poetry install

# 4. Démarrer Kafka et MongoDB (requis pour le service)
docker compose up kafka mongodb -d
```

---

## Démarrage rapide

```bash
# Démarrer le service en local (développement, avec rechargement automatique)
poetry run uvicorn app.main:app --reload --port 8002
```

Le service est disponible sur `http://localhost:8002`.

- **Swagger UI** (documentation interactive) : `http://localhost:8002/docs`
- **Health check** : `http://localhost:8002/health`

### Tester un capteur Radar

```bash
curl -X POST http://localhost:8002/api/v1/sensors/radar \
  -H "X-API-Key: key_radar_001_abc123" \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": 1713033000500,
    "sensor_id": "radar_junction_001",
    "intersection_id": "int_001",
    "lane_number": 2,
    "direction": "north_to_south",
    "vehicle_count": 142,
    "car": 100,
    "truck": 25,
    "motorcycle": 17,
    "avg_speed_kmh": 23.5,
    "occupancy_percent": 78.2,
    "detection_confidence": 0.95
  }'
```

**Réponse attendue :**

```json
{
  "status": "received",
  "sensor_id": "radar_junction_001",
  "zone_id": "int_001",
  "message": "Données reçues et en cours d'agrégation"
}
```

---

## API — Endpoints capteurs

| Méthode | Route | Type capteur | Auth |
|---|---|---|---|
| `POST` | `/api/v1/sensors/radar` | Radar Doppler | `X-API-Key` |
| `POST` | `/api/v1/sensors/smartcamera` | Smart Camera | `X-API-Key` |
| `POST` | `/api/v1/sensors/inductiveloop` | Boucle Inductive | `X-API-Key` |
| `GET` | `/health` | — | Aucune |

### Codes de retour

| Code | Signification |
|---|---|
| `201 Created` | Données reçues et acceptées |
| `400 Bad Request` | Données invalides (valeur hors plage, timestamp expiré) |
| `401 Unauthorized` | Clé API invalide, expirée ou absente |
| `422 Unprocessable Entity` | Structure JSON incorrecte (champ manquant, mauvais type) |

---

## Authentification des capteurs

Chaque capteur IoT est identifié par une **clé API** transmise dans l'en-tête HTTP `X-API-Key`.

Le registre des capteurs est défini dans `config/api_keys.json` :

```json
[
  {
    "api_key": "key_radar_001_abc123",
    "mac_address": "00:1A:2B:3C:4D:5E",
    "sensor_id": "radar_junction_001",
    "sensor_type": "radar",
    "zone_id": "int_001",
    "enabled": true,
    "expires_at": "2027-12-31T23:59:59Z"
  }
]
```

Le service vérifie :
1. La clé existe dans le registre
2. Le capteur est actif (`enabled: true`)
3. La clé n'est pas expirée (`expires_at`)

---

## Formats de données

### Entrée — Radar Doppler (12 champs)

```json
{
  "timestamp": 1713033000500,
  "sensor_id": "radar_junction_001",
  "intersection_id": "int_001",
  "lane_number": 2,
  "direction": "north_to_south",
  "vehicle_count": 142,
  "car": 100,
  "truck": 25,
  "motorcycle": 17,
  "avg_speed_kmh": 23.5,
  "occupancy_percent": 78.2,
  "detection_confidence": 0.95
}
```

### Entrée — Smart Camera (10 champs)

```json
{
  "timestamp": 1713033000500,
  "sensor_id": "smartcam_junction_001",
  "intersection_id": "int_001",
  "vehicle_count": 148,
  "vehicle_avg_speed_kmh": 24.0,
  "occupancy_percent": 76.5,
  "traffic_flow_severity": "normal",
  "anomaly_detected": false,
  "anomaly_type": null,
  "detection_confidence": 0.92
}
```

### Entrée — Boucle Inductive (8 champs)

```json
{
  "timestamp": 1713033000500,
  "sensor_id": "loop_junction_001_lane_1",
  "intersection_id": "int_001",
  "lane_id": "lane_1",
  "vehicle_count": 135,
  "occupancy_percent": 82.3,
  "detection_reliability": 98.5,
  "measurement_interval": 30
}
```

### Sortie — Événement Kafka normalisé (8 champs)

Publié dans le topic `traffic_events_normalized`, partitionné par `zone_id`.

```json
{
  "event_id": "evt_20240414_123000_int001",
  "capteur_id": "radar_junction_001",
  "date_heure": "2024-04-14T12:30:00.500000+00:00",
  "zone_id": "int_001",
  "details": {
    "nombre_vehicule": 142,
    "vitesse_moyenne_kmh": 23.5,
    "taux_occupation": 0.782
  },
  "statut_capteur": "ok"
}
```

### Transformations appliquées

| Champ source | Champ cible | Transformation |
|---|---|---|
| `timestamp` (Unix ms) | `date_heure` | ISO 8601 UTC |
| `occupancy_percent` (0-100%) | `taux_occupation` (0-1) | ÷ 100 |
| Mesures sur 30 secondes | `nombre_vehicule` | Somme |
| Vitesses sur 30 secondes | `vitesse_moyenne_kmh` | Moyenne |

### Statuts capteur

| Statut | Condition |
|---|---|
| `ok` | Données valides, confiance ≥ 0.7 |
| `en_alerte` | Confiance entre 0.5 et 0.7 |
| `hors_ligne` | Aucune donnée depuis > 2 minutes |
| `en_panne` | Plusieurs erreurs de validation simultanées |

---

## Tests

### Lancer les tests

```bash
# Suite complète (avec couverture et JUnit XML)
poetry run pytest tests/ -v

# Tests unitaires uniquement
poetry run pytest tests/unit/ -v

# Tests d'intégration uniquement
poetry run pytest tests/integration/ -v

# Linter
poetry run flake8 app/ tests/
```

### Rapports générés automatiquement

| Fichier | Format | Usage |
|---|---|---|
| `reports/junit.xml` | JUnit XML | CI/CD (GitHub Actions) |
| `reports/coverage.xml` | XML Cobertura | SonarCloud |
| `reports/htmlcov/` | HTML | Lecture locale |

### Résultats actuels

```
46 tests — 46 passed — 0 failed
Coverage : 72%
```

### Organisation des tests

```
tests/
├── conftest.py          # Variables d'env de test (évite connexion Kafka/MongoDB réels)
├── unit/
│   ├── test_normalization_domain.py   # Conversions timestamp, unités (12 tests)
│   ├── test_validation_domain.py      # Règles métier, statuts capteur (14 tests)
│   └── test_aggregation_domain.py     # Fenêtres 30s, sommes, moyennes (9 tests)
└── integration/
    └── test_sensor_controller.py      # Endpoints HTTP bout-en-bout (11 tests)
```

---

## Docker

### Stack locale complète

```bash
# Démarrer Kafka + MongoDB + MS Collecte IoT
docker compose up

# En arrière-plan
docker compose up -d

# Logs en temps réel
docker compose logs -f ms-collecte-iot

# Arrêter tout
docker compose down
```

### Démarrer uniquement l'infrastructure (sans le MS)

```bash
# Utile pendant le développement : on lance le MS avec poetry run
docker compose up kafka mongodb -d
```

### Lancer les tests dans Docker

```bash
docker compose --profile test up ms-collecte-iot-test
```

### Image GHCR

Les images sont automatiquement publiées par le CI/CD sur le GitHub Container Registry :

```
ghcr.io/lee-rudy/ec03_urbanhub/ms-collecte-iot:<tag>
```

Tags disponibles : `main`, `develop`, `sha-<commit>`, `latest` (sur `main` uniquement).

---

## CI/CD

Pipeline GitHub Actions : `.github/workflows/ms-collecte-iot.yml`

**Déclenché sur :**
- `push` vers `main` ou `develop` (si `ms-collecte-iot/**` modifié)
- `pull_request` vers `main`

### Étapes

```
install → test → quality → build → deploy-staging
```

| Étape | Outil | Description |
|---|---|---|
| **install** | Poetry | Installation des dépendances |
| **test** | pytest | Tests + couverture + JUnit XML |
| **quality** | flake8 + SonarCloud + Snyk | Lint, qualité code, sécurité dépendances |
| **build** | Docker + GHCR | Build image + push registry |
| **deploy-staging** | SSH + docker compose | Déploiement automatique (push uniquement) |

### Stratégie de branches

| Branche | CI/CD | Usage |
|---|---|---|
| `feature/ms-collecte-iot` | ❌ | Développement local |
| `post-develop` | ❌ | Partage entre membres de l'équipe |
| `develop` | ✅ Sonar + Snyk | Validation CI/CD |
| `main` | ✅ + deploy | Production |

### Secrets GitHub Actions requis

| Secret | Description |
|---|---|
| `SONAR_TOKEN` | Token SonarCloud |
| `SNYK_TOKEN` | Token Snyk |
| `STAGING_HOST` | Adresse du serveur de staging |
| `STAGING_SSH_KEY` | Clé SSH de déploiement |

---

## Variables d'environnement

Copier `.env.example` en `.env` et adapter les valeurs :

| Variable | Description | Valeur locale |
|---|---|---|
| `APP_HOST` | Adresse d'écoute | `0.0.0.0` |
| `APP_PORT` | Port du service | `8002` |
| `APP_ENV` | Environnement | `development` |
| `KAFKA_BROKERS` | Adresse(s) du broker | `kafka:9092` |
| `KAFKA_TOPIC_OUTPUT` | Topic de sortie | `traffic_events_normalized` |
| `MONGODB_URI` | URI de connexion MongoDB | `mongodb://mongodb:27017` |
| `MONGODB_DB_NAME` | Nom de la base | `urbanhub_collecte` |
| `API_KEYS_CONFIG_PATH` | Chemin vers le registre capteurs | `./config/api_keys.json` |
| `DATA_RETENTION_DAYS` | Rétention RGPD (jours) | `30` |
| `LOG_LEVEL` | Niveau de log | `INFO` |

---

## Conformité RGPD

- Aucune **plaque d'immatriculation** ni **image brute** traitée ou stockée
- Aucune **donnée personnelle** dans les événements Kafka ou les logs
- Rétention des événements MongoDB limitée à `DATA_RETENTION_DAYS` jours
- Suppression automatique déclenchée via `sensor_repository.delete_events_older_than_days()`

---

## Liens

- [Repo principal](https://github.com/Lee-Rudy/EC03_UrbanHub)
- [Pipeline CI/CD](.github/workflows/ms-collecte-iot.yml)
- [CLAUDE.md — Spécifications complètes](CLAUDE.md)
- [Swagger UI](http://localhost:8002/docs) *(service démarré requis)*
