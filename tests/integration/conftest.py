"""Shared fixtures for PostgreSQL integration tests."""

from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from testcontainers.postgres import PostgresContainer

from app.core.database import get_db
from app.main import app


@pytest.fixture(scope="session")
def postgres_engine() -> Generator[Engine, None, None]:
    """Start a disposable PostgreSQL container and apply init.sql."""
    try:
        with PostgresContainer("postgres:16-alpine") as postgres:
            engine = create_engine(postgres.get_connection_url(), future=True)
            with engine.begin() as connection:
                connection.exec_driver_sql(Path("init.sql").read_text())
            yield engine
            engine.dispose()
    except Exception as exc:
        pytest.skip(f"PostgreSQL Testcontainers unavailable: {exc}")


@pytest.fixture()
def postgres_session(postgres_engine: Engine) -> Generator[Session, None, None]:
    """Create a database session bound to the Testcontainers engine."""
    testing_session = sessionmaker(
        bind=postgres_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        class_=Session,
    )
    session = testing_session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def integration_client(
    postgres_session: Session,
) -> Generator[TestClient, None, None]:
    """Create a TestClient that uses the Testcontainers database session."""
    def override_get_db() -> Generator[Session, None, None]:
        yield postgres_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
