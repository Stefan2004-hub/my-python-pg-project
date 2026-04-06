"""API route tests."""

from collections.abc import Generator

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.main import app
from app.models import Base
from app.repositories import CustomerRepository
from app.schemas.customer import CustomerCreate


@pytest.fixture()
def api_db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    testing_session = sessionmaker(
        bind=engine,
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
        Base.metadata.drop_all(engine)


@pytest.fixture()
def client(api_db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield api_db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _create_customer(db_session: Session, email: str = "api@example.com"):
    return CustomerRepository(db_session).create(
        CustomerCreate(
            first_name="API",
            last_name="Customer",
            email=email,
            phone=None,
            address=None,
            city=None,
            state=None,
            zip_code=None,
        )
    )


def test_category_routes_crud_and_list_envelope(client: TestClient):
    create_response = client.post(
        "/categories",
        json={"name": "Hardware", "description": "Tools"},
    )
    assert create_response.status_code == 201
    category_id = create_response.json()["id"]

    list_response = client.get("/categories")
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1
    assert list_response.json()["items"][0]["name"] == "Hardware"

    update_response = client.put(
        f"/categories/{category_id}",
        json={"description": "Updated"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["description"] == "Updated"

    delete_response = client.delete(f"/categories/{category_id}")
    assert delete_response.status_code == 204
    assert client.get(f"/categories/{category_id}").status_code == 404


def test_product_routes_crud_filter_search_and_delete(client: TestClient):
    category = client.post("/categories", json={"name": "Books"}).json()
    client.post(
        "/products",
        json={
            "name": "Python Handbook",
            "description": "Programming guide",
            "price": "25.00",
            "category_id": category["id"],
        },
    )
    other = client.post(
        "/products",
        json={
            "name": "Desk Lamp",
            "description": "Office light",
            "price": "15.00",
            "category_id": None,
        },
    ).json()

    filtered = client.get(f"/products?category_id={category['id']}&search=python")
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1
    assert filtered.json()["items"][0]["name"] == "Python Handbook"

    updated = client.put(f"/products/{other['id']}", json={"price": "17.50"})
    assert updated.status_code == 200
    assert updated.json()["price"] == "17.50"

    assert client.delete(f"/products/{other['id']}").status_code == 204


def test_order_routes_create_list_status_update_and_delete(
    client: TestClient,
    api_db_session: Session,
):
    customer = _create_customer(api_db_session)
    product = client.post(
        "/products",
        json={
            "name": "Monitor",
            "description": "Display",
            "price": "100.00",
            "category_id": None,
        },
    ).json()

    created = client.post(
        "/orders",
        json={
            "customer_id": customer.id,
            "status": "pending",
            "items": [{"product_id": product["id"], "quantity": 2}],
        },
    )
    assert created.status_code == 201
    order = created.json()
    assert order["total_amount"] == "200.00"
    assert order["items"][0]["unit_price"] == "100.00"
    assert order["items"][0]["line_total"] == "200.00"

    listed = client.get("/orders?status=pending")
    assert listed.status_code == 200
    assert listed.json()["total"] == 1

    updated = client.patch(
        f"/orders/{order['id']}/status",
        json={"status": "shipped"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "shipped"

    assert client.delete(f"/orders/{order['id']}").status_code == 204


def test_report_routes_return_json_arrays(client: TestClient, api_db_session: Session):
    category = client.post("/categories", json={"name": "Furniture"}).json()
    customer = _create_customer(api_db_session, email="reports-api@example.com")
    product = client.post(
        "/products",
        json={
            "name": "Chair",
            "description": "Office chair",
            "price": "55.00",
            "category_id": category["id"],
        },
    ).json()
    client.post(
        "/orders",
        json={
            "customer_id": customer.id,
            "status": "pending",
            "items": [{"product_id": product["id"], "quantity": 2}],
        },
    )

    endpoints = [
        "/reports/sales-by-product",
        "/reports/sales-by-category",
        "/reports/top-products?limit=5",
        "/reports/daily-sales",
        f"/reports/customers/{customer.id}/orders",
    ]
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert response.json()
