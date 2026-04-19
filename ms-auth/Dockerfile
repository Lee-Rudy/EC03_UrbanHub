FROM python:3.13-slim

WORKDIR /app

ENV POETRY_REQUESTS_TIMEOUT=600 \
    POETRY_NO_INTERACTION=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

# Le projet Poetry est dans le dossier `authentification/`
# Note: on ne copie pas `poetry.lock` ici, car il peut être désynchronisé
# lors des itérations. Poetry résout alors depuis `pyproject.toml`.
COPY authentification/pyproject.toml ./

RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction

# On copie uniquement le code utile (sans écraser le lock généré dans l'image).
COPY authentification/main.py ./main.py
COPY authentification/src ./src

EXPOSE 8001

ENV PYTHONPATH=/app/src

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]