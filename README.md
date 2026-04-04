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

## Start Local PostgreSQL
Use Docker Compose to start the local PostgreSQL service:

```bash
docker compose up -d postgres
```

If `init.sql` is present in the repository root, PostgreSQL will execute it during first-time container initialization.

## Planned Run Command
Application startup will be added in a later phase. The expected command is:

```bash
uvicorn app.main:app --reload
```

## Planned Test Command
Tests will be added in later phases. The expected command is:

```bash
pytest
```
