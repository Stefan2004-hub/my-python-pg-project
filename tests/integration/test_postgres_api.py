"""PostgreSQL integration tests."""

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.repositories import CustomerRepository
from app.schemas.customer import CustomerCreate


def _create_customer(db_session: Session, email: str = "integration@example.com"):
    return CustomerRepository(db_session).create(
        CustomerCreate(
            first_name="Integration",
            last_name="Customer",
            email=email,
            phone=None,
            address=None,
            city=None,
            state=None,
            zip_code=None,
        )
    )


def test_init_sql_creates_expected_tables(postgres_session: Session):
    rows = postgres_session.execute(
        text(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
            """
        )
    )
    table_names = {row.table_name for row in rows}

    assert {
        "categories",
        "customers",
        "order_items",
        "orders",
        "products",
    }.issubset(table_names)


def test_health_endpoint_uses_postgres_container(integration_client):
    response = integration_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "application": "up",
        "database": "up",
    }


def test_api_order_and_report_flow_against_postgres(
    integration_client,
    postgres_session: Session,
):
    customer = _create_customer(postgres_session)
    category = integration_client.post(
        "/categories",
        json={"name": "Integration Category", "description": None},
    ).json()
    product = integration_client.post(
        "/products",
        json={
            "name": "Integration Product",
            "description": "PostgreSQL-backed product",
            "price": "12.50",
            "stock_quantity": 4,
            "category_id": category["id"],
        },
    ).json()

    order_response = integration_client.post(
        "/orders",
        json={
            "customer_id": customer.id,
            "status": "pending",
            "items": [{"product_id": product["id"], "quantity": 4}],
        },
    )
    report_response = integration_client.get("/reports/sales-by-product")

    assert order_response.status_code == 201
    assert order_response.json()["total_amount"] == "50.00"
    assert report_response.status_code == 200
    assert report_response.json()[0]["product_name"] == "Integration Product"
    assert report_response.json()[0]["total_sales"] == 50.0
