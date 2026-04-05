# My Python PG Project

This repository bootstraps a FastAPI-based e-commerce service with a Spring-like architecture. The planned stack uses FastAPI, SQLAlchemy, PostgreSQL, Pydantic, and Pandas for reporting.

## Prerequisites
- Python 3.11 or newer
- Docker and Docker Compose

## Install Dependencies
Create and activate a virtual environment, then install the project in editable mode with development dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

After that you can verify the app with:

```bash
uvicorn app.main:app --reload
```

and, with PostgreSQL running via Docker Compose, check:

```bash
curl http://127.0.0.1:8000/health
```
## Runtime Configuration
The application reads configuration from environment variables. Local defaults are already aligned with the PostgreSQL container in `docker-compose.yml`.

- `APP_NAME`
- `APP_ENV`
- `DEBUG`
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`

## Start Local PostgreSQL
Use Docker Compose to start the local PostgreSQL service:

```bash
docker compose up -d postgres
```

If `init.sql` is present in the repository root, PostgreSQL will execute it during first-time container initialization.

## Planned Run Command
Start the FastAPI application with:

```bash
uvicorn app.main:app --reload
```

## Current Health Check
Once the app and database are running, verify the service with:

```bash
curl http://127.0.0.1:8000/health
```

The endpoint returns success only when the application is up and PostgreSQL is reachable.

## Current Test Command
Use `pytest` for the test suite as it grows in later phases:

```bash
pytest
```

## Generate an ERD
The repository includes [`generate_erd.py`](/home/dstefan/Documents/tools/my-python-pg-project/generate_erd.py) for generating an entity relationship diagram from the SQLAlchemy models.

This generates `entity_relation.png` from the SQLAlchemy model metadata in `app.models`. It does not inspect a live database.

Install development dependencies first:

```bash
pip install -e ".[dev]"
```

Make sure GraphViz is installed on the machine. On Fedora:

```bash
sudo dnf install graphviz
```

Verify the model metadata loads:

```bash
python -c "from app.models import Base; print(sorted(Base.metadata.tables.keys()))"
```

Then generate the ERD:

```bash
python generate_erd.py
```

If the command succeeds, the output file will be `entity_relation.png` in the project root.

Common failure causes are missing development dependencies or GraphViz not being installed and available on `PATH`.
