"""Repository layer tests."""

from datetime import datetime, UTC
from decimal import Decimal

import pytest

from app.core.exceptions import DomainValidationError, NotFoundError
from app.models import Order, OrderItem
from app.repositories import (
    CategoryRepository,
    CustomerRepository,
    OrderRepository,
    ProductRepository,
)
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.schemas.order import OrderItemPricedCreate, OrderPricedCreate
from app.schemas.product import ProductCreate, ProductUpdate


def test_category_repository_crud(db_session):
    repository = CategoryRepository(db_session)

    created = repository.create(
        CategoryCreate(name="Electronics", description="Devices")
    )
    fetched = repository.get_by_id(created.id)
    updated = repository.update(
        created.id,
        CategoryUpdate(description="Updated description"),
    )
    items, total = repository.list()

    assert fetched.id == created.id
    assert updated.description == "Updated description"
    assert total == 1
    assert items[0].name == "Electronics"

    repository.delete(created.id)

    with pytest.raises(NotFoundError):
        repository.get_by_id(created.id)


def test_product_repository_filters_search_and_pagination(db_session):
    category_repository = CategoryRepository(db_session)
    product_repository = ProductRepository(db_session)

    category = category_repository.create(
        CategoryCreate(name="Books", description="Printed books")
    )
    product_repository.create(
        ProductCreate(
            name="Python 101",
            description="Learn Python",
            price=Decimal("29.99"),
            category_id=category.id,
        )
    )
    product_repository.create(
        ProductCreate(
            name="SQL Handbook",
            description="Database guide",
            price=Decimal("39.99"),
            category_id=category.id,
        )
    )
    product_repository.create(
        ProductCreate(
            name="Laptop Stand",
            description="Desk accessory",
            price=Decimal("19.99"),
            category_id=None,
        )
    )

    filtered_items, filtered_total = product_repository.list(category_id=category.id)
    searched_items, searched_total = product_repository.list(search="python")
    paged_items, paged_total = product_repository.list(page=2, page_size=1)

    assert filtered_total == 2
    assert len(filtered_items) == 2
    assert searched_total == 1
    assert searched_items[0].name == "Python 101"
    assert paged_total == 3
    assert len(paged_items) == 1


def test_product_repository_update_and_delete(db_session):
    product_repository = ProductRepository(db_session)
    product = product_repository.create(
        ProductCreate(
            name="Mouse",
            description="Wireless mouse",
            price=Decimal("12.99"),
            category_id=None,
        )
    )

    updated = product_repository.update(
        product.id,
        ProductUpdate(price=Decimal("14.99")),
    )
    assert updated.price == Decimal("14.99")

    product_repository.delete(product.id)
    with pytest.raises(NotFoundError):
        product_repository.get_by_id(product.id)


def test_customer_repository_crud_and_get_by_email(db_session):
    repository = CustomerRepository(db_session)

    customer = repository.create(
        CustomerCreate(
            first_name="Ada",
            last_name="Lovelace",
            email="ada@example.com",
            phone="123456",
            address="1 Main St",
            city="London",
            state="LDN",
            zip_code="12345",
        )
    )

    by_email = repository.get_by_email("ada@example.com")
    updated = repository.update(
        customer.id,
        CustomerUpdate(city="Athens"),
    )
    items, total = repository.list()

    assert by_email is not None
    assert by_email.id == customer.id
    assert updated.city == "Athens"
    assert total == 1
    assert items[0].email == "ada@example.com"

    repository.delete(customer.id)
    with pytest.raises(NotFoundError):
        repository.get_by_id(customer.id)


def test_order_repository_creates_nested_items_and_eager_loads_relations(db_session):
    customer_repository = CustomerRepository(db_session)
    product_repository = ProductRepository(db_session)
    order_repository = OrderRepository(db_session)

    customer = customer_repository.create(
        CustomerCreate(
            first_name="Grace",
            last_name="Hopper",
            email="grace@example.com",
            phone=None,
            address=None,
            city=None,
            state=None,
            zip_code=None,
        )
    )
    product = product_repository.create(
        ProductCreate(
            name="Monitor",
            description="27 inch display",
            price=Decimal("199.99"),
            category_id=None,
        )
    )

    created = order_repository.create_order(
        OrderPricedCreate(
            customer_id=customer.id,
            order_date=datetime(2026, 4, 5, 12, 0, tzinfo=UTC),
            total_amount=Decimal("399.98"),
            status="pending",
            items=[
                OrderItemPricedCreate(
                    product_id=product.id,
                    quantity=2,
                    unit_price=Decimal("199.99"),
                    line_total=Decimal("399.98"),
                )
            ],
        )
    )

    assert created.customer.email == "grace@example.com"
    assert len(created.order_items) == 1
    assert created.order_items[0].product.name == "Monitor"
    assert created.order_items[0].line_total == Decimal("399.98")


def test_order_repository_filters_pagination_and_status_updates(db_session):
    customer_repository = CustomerRepository(db_session)
    product_repository = ProductRepository(db_session)
    order_repository = OrderRepository(db_session)

    customer = customer_repository.create(
        CustomerCreate(
            first_name="Linus",
            last_name="Torvalds",
            email="linus@example.com",
            phone=None,
            address=None,
            city=None,
            state=None,
            zip_code=None,
        )
    )
    product = product_repository.create(
        ProductCreate(
            name="Keyboard",
            description="Mechanical keyboard",
            price=Decimal("89.00"),
            category_id=None,
        )
    )

    for index, status in enumerate(["pending", "pending", "shipped"], start=1):
        order_repository.create_order(
            OrderPricedCreate(
                customer_id=customer.id,
                order_date=datetime(2026, 4, index, 9, 0, tzinfo=UTC),
                total_amount=Decimal("89.00"),
                status=status,
                items=[
                    OrderItemPricedCreate(
                        product_id=product.id,
                        quantity=1,
                        unit_price=Decimal("89.00"),
                        line_total=Decimal("89.00"),
                    )
                ],
            )
        )

    pending_items, pending_total = order_repository.list(status="pending")
    paged_items, paged_total = order_repository.list(page=2, page_size=1)
    updated = order_repository.update_status(pending_items[0].id, "completed")

    assert pending_total == 2
    assert len(pending_items) == 2
    assert paged_total == 3
    assert len(paged_items) == 1
    assert updated.status == "completed"


def test_order_repository_validates_missing_entities(db_session):
    order_repository = OrderRepository(db_session)

    with pytest.raises(NotFoundError, match="Customer not found"):
        order_repository.create_order(
            OrderPricedCreate(
                customer_id=999,
                order_date=datetime(2026, 4, 5, 12, 0, tzinfo=UTC),
                total_amount=Decimal("10.00"),
                status="pending",
                items=[
                    OrderItemPricedCreate(
                        product_id=1,
                        quantity=1,
                        unit_price=Decimal("10.00"),
                        line_total=Decimal("10.00"),
                    )
                ],
            )
        )


def test_order_repository_rejects_empty_item_list(db_session):
    customer_repository = CustomerRepository(db_session)
    order_repository = OrderRepository(db_session)
    customer = customer_repository.create(
        CustomerCreate(
            first_name="Empty",
            last_name="Order",
            email="empty@example.com",
            phone=None,
            address=None,
            city=None,
            state=None,
            zip_code=None,
        )
    )

    with pytest.raises(DomainValidationError, match="at least one item"):
        order_repository.create_order(
            OrderPricedCreate(
                customer_id=customer.id,
                order_date=datetime(2026, 4, 5, 12, 0, tzinfo=UTC),
                total_amount=Decimal("0.00"),
                status="pending",
                items=[],
            )
        )


def test_order_repository_delete_removes_order_and_items(db_session):
    customer_repository = CustomerRepository(db_session)
    product_repository = ProductRepository(db_session)
    order_repository = OrderRepository(db_session)

    customer = customer_repository.create(
        CustomerCreate(
            first_name="Delete",
            last_name="Case",
            email="delete@example.com",
            phone=None,
            address=None,
            city=None,
            state=None,
            zip_code=None,
        )
    )
    product = product_repository.create(
        ProductCreate(
            name="Chair",
            description="Office chair",
            price=Decimal("55.00"),
            category_id=None,
        )
    )
    order = order_repository.create_order(
        OrderPricedCreate(
            customer_id=customer.id,
            order_date=datetime(2026, 4, 5, 12, 0, tzinfo=UTC),
            total_amount=Decimal("55.00"),
            status="pending",
            items=[
                OrderItemPricedCreate(
                    product_id=product.id,
                    quantity=1,
                    unit_price=Decimal("55.00"),
                    line_total=Decimal("55.00"),
                )
            ],
        )
    )

    order_repository.delete(order.id)

    with pytest.raises(NotFoundError):
        order_repository.get_by_id(order.id)
    assert db_session.query(Order).count() == 0
    assert db_session.query(OrderItem).count() == 0
