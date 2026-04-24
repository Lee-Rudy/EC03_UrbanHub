name: MS Collecte IoT — CI/CD

on:
  push:
    branches:
      - main
      - develop
    paths:
      - "ms-collecte-iot/**"
  pull_request:
    branches:
      - main
    paths:
      - "ms-collecte-iot/**"

defaults:
  run:
    working-directory: ms-collecte-iot

jobs:

  # ──────────────────────────────────────────────
  # 1. INSTALL
  # ──────────────────────────────────────────────
  install:
    name: Install dependencies
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install Poetry
        uses: snok/install-poetry@v1
        with:
          version: "1.8.2"
          virtualenvs-create: true
          virtualenvs-in-project: true

      - name: Install dependencies
        run: poetry install --no-root

  # ──────────────────────────────────────────────
  # 2. TEST — unit + integration + coverage
  # ──────────────────────────────────────────────
  test:
    name: Tests (unit + integration)
    runs-on: ubuntu-latest
    needs: install
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install Poetry
        uses: snok/install-poetry@v1
        with:
          version: "1.8.2"
          virtualenvs-create: true
          virtualenvs-in-project: true

      - name: Install dependencies
        run: poetry install --no-root

      - name: Create reports directory
        run: mkdir -p reports

      - name: Run all tests with coverage
        # Génère junit.xml (CI) + coverage.xml (SonarCloud) + htmlcov (lisible)
        # --cov-fail-under=75 fait échouer le pipeline si la couverture passe sous 75%
        run: |
          poetry run pytest tests/ -v \
            --junitxml=reports/junit.xml \
            --cov=app \
            --cov-report=xml:reports/coverage.xml \
            --cov-report=term-missing \
            --cov-fail-under=75

      - name: Upload coverage artifact
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: ms-collecte-iot/reports/coverage.xml

      - name: Upload JUnit test results
        uses: actions/upload-artifact@v4
        if: always()    # Publier même si les tests échouent (pour diagnostic)
        with:
          name: junit-results
          path: ms-collecte-iot/reports/junit.xml

  # ──────────────────────────────────────────────
  # 3. QUALITY — flake8 + sonar + snyk
  # ──────────────────────────────────────────────
  quality:
    name: Quality & Security
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install Poetry
        uses: snok/install-poetry@v1
        with:
          version: "1.8.2"
          virtualenvs-create: true
          virtualenvs-in-project: true

      - name: Install dependencies
        run: poetry install --no-root

      - name: Flake8 lint
        run: poetry run flake8 app/ tests/

      - name: Download coverage report
        uses: actions/download-artifact@v4
        with:
          name: coverage-report
          path: ms-collecte-iot/reports/

      - name: SonarCloud scan
        uses: SonarSource/sonarcloud-github-action@master
        with:
          projectBaseDir: .
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}

      - name: Snyk security scan
        uses: snyk/actions/python@master
        with:
          args: --file=ms-collecte-iot/pyproject.toml --severity-threshold=high
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

  # ──────────────────────────────────────────────
  # 4. BUILD — docker build + push vers GHCR
  # ──────────────────────────────────────────────
  build:
    name: Docker build & push (GHCR)
    runs-on: ubuntu-latest
    needs: quality
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4

      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract Docker metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/lee-rudy/ec03_urbanhub/ms-collecte-iot
          tags: |
            type=ref,event=branch
            type=sha,prefix=sha-
            type=raw,value=latest,enable=${{ github.ref == 'refs/heads/main' }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: ms-collecte-iot
          dockerfile: ms-collecte-iot/Dockerfile
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}

  # ──────────────────────────────────────────────
  # 5. DEPLOY STAGING — docker compose up
  #    Déclenché uniquement sur push (pas sur PR)
  # ──────────────────────────────────────────────
  deploy-staging:
    name: Deploy to staging
    runs-on: ubuntu-latest
    needs: build
    if: github.event_name == 'push'
    steps:
      - uses: actions/checkout@v4

      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Deploy via docker compose
        # Injecte les variables d'environnement de staging dans le .env
        # Les secrets sont définis dans GitHub → Settings → Secrets → Actions
        run: |
          echo "APP_ENV=staging" > .env
          echo "APP_PORT=8002" >> .env
          echo "KAFKA_BROKERS=${{ secrets.STAGING_KAFKA_BROKERS }}" >> .env
          echo "KAFKA_TOPIC_OUTPUT=traffic_events_normalized" >> .env
          echo "MONGODB_URI=${{ secrets.STAGING_MONGODB_URI }}" >> .env
          echo "MONGODB_DB_NAME=urbanhub_collecte" >> .env
          echo "API_KEYS_CONFIG_PATH=./config/api_keys.json" >> .env
          echo "DATA_RETENTION_DAYS=30" >> .env
          echo "LOG_LEVEL=INFO" >> .env
          docker compose up -d --pull always
        working-directory: ms-collecte-iot
