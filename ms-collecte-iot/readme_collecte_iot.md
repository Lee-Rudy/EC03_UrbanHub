# MS Collecte IoT

Microservice de collecte de données IoT pour le projet **UrbanHub** — reçoit les données des capteurs urbains via MQTT et les expose via une API REST.

![CI/CD](https://github.com/Lee-Rudy/EC03_UrbanHub/actions/workflows/ms-collecte-iot.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green)
![Docker](https://img.shields.io/badge/Docker-ready-blue)

---

## Sommaire

- [Architecture](#architecture)
- [Stack technique](#stack-technique)
- [Installation locale](#installation-locale)
- [Tests](#tests)
- [Docker](#docker)
- [CI/CD](#cicd)
- [Variables d'environnement](#variables-denvironnement)
- [API](#api)

---

## Architecture

Ce microservice suit l'architecture en couches définie par l'équipe :

```
ms-collecte-iot/
├── app/
│   ├── controllers/      # Endpoints FastAPI (routeurs HTTP)
│   ├── domains/          # Entités métier et logique de domaine
│   ├── dtos/             # Data Transfer Objects (schémas d'entrée/sortie)
│   ├── repositories/     # Accès aux données (MQTT, stockage)
│   └── main.py           # Point d'entrée de l'application
├── tests/
│   ├── test_unit.py      # Tests unitaires
│   └── test_integration.py # Tests d'intégration HTTP
├── Dockerfile            # Image de production
├── Dockerfile.test       # Image de test (CI/CD)
├── docker-compose.yml    # Stack locale (service + broker MQTT)
└── pyproject.toml        # Dépendances (Poetry)
```

### Flux de données

```
Capteurs IoT → MQTT Broker → MS Collecte IoT → API REST → Autres microservices
```

---

## Stack technique

| Composant | Technologie | Version |
|---|---|---|
| Language | Python | 3.11 |
| Framework API | FastAPI | 0.110 |
| Serveur ASGI | Uvicorn | 0.29 |
| Broker MQTT | paho-mqtt | 2.0 |
| Gestion deps | Poetry | 1.8.2 |
| Containerisation | Docker | - |
| Tests | pytest + pytest-cov | 8.1 |
| Linter | flake8 | 7.0 |

---

## Installation locale

### Prérequis

- Python 3.11+
- [Poetry](https://python-poetry.org/docs/#installation)
- Docker + Docker Compose

### Étapes

```bash
# 1. Cloner le repo (si pas déjà fait)
git clone https://github.com/Lee-Rudy/EC03_UrbanHub.git
cd EC03_UrbanHub/ms-collecte-iot

# 2. Copier les variables d'environnement
cp .env.example .env

# 3. Installer les dépendances
poetry install

# 4. Lancer le service en local
poetry run uvicorn app.main:app --reload --port 8001
```

Le service est disponible sur `http://localhost:8001`.

---

## Tests

```bash
# Tous les tests
poetry run pytest tests/ -v

# Avec rapport de couverture
poetry run pytest tests/ -v --cov=app --cov-report=term-missing

# Tests unitaires uniquement
poetry run pytest tests/test_unit.py -v

# Tests d'intégration uniquement
poetry run pytest tests/test_integration.py -v

# Linter
poetry run flake8 app/ tests/
```

Couverture minimale requise : **75%** (vérifiée par le CI/CD).

---

## Docker

### Image de production

```bash
# Build
docker build -t ms-collecte-iot:local .

# Run
docker run -p 8001:8000 --env-file .env ms-collecte-iot:local
```

### Image de test

```bash
# Build + run des tests dans le container
docker build -f Dockerfile.test -t ms-collecte-iot-test:local .
docker run --rm ms-collecte-iot-test:local
```

### Stack complète (service + broker MQTT)

```bash
# Démarrer le service + broker MQTT
docker compose up

# Démarrer uniquement les tests
docker compose --profile test up ms-collecte-iot-test
```

### Image sur GHCR

Les images sont automatiquement publiées sur le GitHub Container Registry :

```
ghcr.io/lee-rudy/ec03_urbanhub/ms-collecte-iot:<tag>
```

Tags disponibles : `main`, `develop`, `sha-<commit>`, `latest` (sur `main` uniquement).

---

## CI/CD

Pipeline GitHub Actions déclenché sur :
- **`push`** sur `main` ou `develop` (si `ms-collecte-iot/**` modifié)
- **`pull_request`** vers `main`

### Étapes du pipeline

```
install → test → quality → build → deploy-staging
```

| Étape | Description |
|---|---|
| **install** | Installation des dépendances via Poetry |
| **test** | Tests unitaires + intégration + rapport de couverture |
| **quality** | flake8 (lint) + SonarCloud (qualité) + Snyk (sécurité) |
| **build** | Build Docker + push vers GHCR |
| **deploy-staging** | `docker compose up` en staging (push uniquement) |

### Stratégie de branches

| Branche | CI/CD | Usage |
|---|---|---|
| `feature/ms-collecte-iot` | ❌ | Développement |
| `post-develop` | ❌ | Partage d'avancement entre membres |
| `develop` | ✅ Sonar + Snyk | Validation CI/CD |
| `main` | ✅ + deploy | Production |

---

## Variables d'environnement

Copier `.env.example` en `.env` et adapter :

| Variable | Description | Défaut |
|---|---|---|
| `ENVIRONMENT` | Environnement d'exécution | `local` |
| `MQTT_HOST` | Adresse du broker MQTT | `mqtt-broker` |
| `MQTT_PORT` | Port du broker MQTT | `1883` |

### Secrets GitHub Actions requis

| Secret | Description |
|---|---|
| `SONAR_TOKEN` | Token SonarCloud |
| `SNYK_TOKEN` | Token Snyk |
| `STAGING_MQTT_HOST` | Adresse broker MQTT en staging |

---

## API

### Endpoints

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/health` | Vérification de l'état du service |

### Exemple

```bash
curl http://localhost:8001/health
```

```json
{
  "status": "ok",
  "service": "ms-collecte-iot"
}
```

La documentation interactive (Swagger) est disponible sur `http://localhost:8001/docs`.

---

## Liens

- [Repo principal](https://github.com/Lee-Rudy/EC03_UrbanHub)
- [MS Auth (référence)](https://github.com/Lee-Rudy/EC03_UrbanHub/tree/feature/ms-auth)
- [Pipeline CI/CD](.github/workflows/ms-collecte-iot.yml)
