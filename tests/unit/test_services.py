"""Service layer tests."""

from datetime import UTC, datetime
from decimal import Decimal
import json

import pytest

from app.core.exceptions import DomainValidationError, NotFoundError
from app.schemas.category import CategoryCreate
from app.schemas.customer import CustomerCreate
from app.schemas.order import OrderCreate, OrderItemCreate
from app.schemas.product import ProductCreate, ProductUpdate
from app.services import (
    CategoryService,
    OrderService,
    ProductService,
    ReportService,
)


def _customer_payload(email: str) -> CustomerCreate:
    return CustomerCreate(
        first_name="Test",
        last_name="Customer",
        email=email,
        phone=None,
        address=None,
        city=None,
        state=None,
        zip_code=None,
    )


def _order_payload(customer_id: int, product_id: int, quantity: int = 1) -> OrderCreate:
    return OrderCreate(
        customer_id=customer_id,
        order_date=datetime(2026, 4, 7, 12, 0, tzinfo=UTC),
        total_amount=Decimal("0.01"),
        status="pending",
        items=[
            OrderItemCreate(
                product_id=product_id,
                quantity=quantity,
                unit_price=Decimal("0.01"),
                line_total=Decimal("0.01"),
            )
        ],
    )


def test_category_and_product_services_wrap_crud(db_session):
    category_service = CategoryService(db_session)
    product_service = ProductService(db_session)

    category = category_service.create(CategoryCreate(name="Accessories"))
    product = product_service.create(
        ProductCreate(
            name="USB Cable",
            description="Braided cable",
            price=Decimal("8.50"),
            category_id=category.id,
        )
    )
    updated = product_service.update(
        product.id,
        ProductUpdate(price=Decimal("9.25")),
    )
    items, total = product_service.list(category_id=category.id, search="usb")

    assert updated.price == Decimal("9.25")
    assert total == 1
    assert items[0].id == product.id

    product_service.delete(product.id)
    with pytest.raises(NotFoundError):
        product_service.get_by_id(product.id)


def test_product_service_rejects_negative_prices(db_session):
    product_service = ProductService(db_session)

    with pytest.raises(DomainValidationError, match="price"):
        product_service.create(
            ProductCreate(
                name="Invalid",
                description=None,
                price=Decimal("-1.00"),
                category_id=None,
            )
        )


def test_order_service_recomputes_totals_from_product_prices(db_session):
    from app.repositories import CustomerRepository

    product_service = ProductService(db_session)
    order_service = OrderService(db_session)
    customer = CustomerRepository(db_session).create(_customer_payload("orders@example.com"))
    product = product_service.create(
        ProductCreate(
            name="Desk",
            description="Standing desk",
            price=Decimal("120.00"),
            category_id=None,
        )
    )

    order = order_service.create_order(_order_payload(customer.id, product.id, quantity=3))

    assert order.total_amount == Decimal("360.00")
    assert order.order_items[0].unit_price == Decimal("120.00")
    assert order.order_items[0].line_total == Decimal("360.00")


def test_order_service_rejects_non_positive_quantities(db_session):
    from app.repositories import CustomerRepository

    product_service = ProductService(db_session)
    order_service = OrderService(db_session)
    customer = CustomerRepository(db_session).create(_customer_payload("invalid@example.com"))
    product = product_service.create(
        ProductCreate(
            name="Mouse Pad",
            description=None,
            price=Decimal("4.00"),
            category_id=None,
        )
    )

    with pytest.raises(DomainValidationError, match="quantity"):
        order_service.create_order(_order_payload(customer.id, product.id, quantity=0))


def test_order_service_list_status_update_and_delete(db_session):
    from app.repositories import CustomerRepository

    product_service = ProductService(db_session)
    order_service = OrderService(db_session)
    customer = CustomerRepository(db_session).create(_customer_payload("status@example.com"))
    product = product_service.create(
        ProductCreate(
            name="Headphones",
            description=None,
            price=Decimal("60.00"),
            category_id=None,
        )
    )
    order = order_service.create_order(_order_payload(customer.id, product.id))

    pending_orders, total = order_service.list(status="pending")
    updated = order_service.update_status(order.id, "shipped")
    order_service.delete(order.id)

    assert total == 1
    assert pending_orders[0].id == order.id
    assert updated.status == "shipped"
    with pytest.raises(NotFoundError):
        order_service.get_by_id(order.id)


def test_report_service_returns_json_ready_core_reports(db_session):
    from app.repositories import CustomerRepository

    category_service = CategoryService(db_session)
    product_service = ProductService(db_session)
    order_service = OrderService(db_session)
    report_service = ReportService(db_session)

    category = category_service.create(CategoryCreate(name="Furniture"))
    customer = CustomerRepository(db_session).create(_customer_payload("reports@example.com"))
    product = product_service.create(
        ProductCreate(
            name="Chair",
            description="Office chair",
            price=Decimal("55.00"),
            category_id=category.id,
        )
    )
    order_service.create_order(_order_payload(customer.id, product.id, quantity=2))

    reports = {
        "sales_by_product": report_service.sales_by_product(),
        "sales_by_category": report_service.sales_by_category(),
        "top_products": report_service.top_products(limit=5),
        "daily_sales": report_service.daily_sales(),
        "customer_order_history": report_service.customer_order_history(customer.id),
    }

    assert reports["sales_by_product"][0]["product_name"] == "Chair"
    assert reports["sales_by_product"][0]["total_sales"] == 110.0
    assert reports["sales_by_category"][0]["category_name"] == "Furniture"
    assert reports["top_products"][0]["quantity_sold"] == 2
    assert reports["daily_sales"][0]["total_sales"] == 110.0
    assert reports["customer_order_history"][0]["customer_email"] == "reports@example.com"
    json.dumps(reports)
