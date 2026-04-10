"""Business logic for orders."""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import DomainValidationError
from app.models import Order
from app.repositories import OrderRepository, ProductRepository
from app.schemas.order import (
    OrderCreate,
    OrderItemPricedCreate,
    OrderPricedCreate,
    OrderUpdate,
)


class OrderService:
    """Service API for order use cases."""

    def __init__(self, db: Session) -> None:
        self.order_repository = OrderRepository(db)
        self.product_repository = ProductRepository(db)

    def create_order(self, payload: OrderCreate) -> Order:
        if not payload.items:
            raise DomainValidationError("Order must include at least one item")

        self.order_repository.validate_customer_exists(payload.customer_id)

        products = {}
        requested_quantities: dict[int, int] = {}
        for item in payload.items:
            if item.quantity <= 0:
                raise DomainValidationError("Order item quantity must be positive")

            product = products.get(item.product_id)
            if product is None:
                product = self.product_repository.get_by_id(item.product_id)
                products[item.product_id] = product
            requested_quantities[item.product_id] = (
                requested_quantities.get(item.product_id, 0) + item.quantity
            )

        for product_id, requested_quantity in requested_quantities.items():
            product = products[product_id]
            if requested_quantity > product.stock_quantity:
                raise DomainValidationError(
                    f"Insufficient stock for product {product_id}"
                )

        normalized_items: list[OrderItemPricedCreate] = []
        total_amount = Decimal("0.00")
        for item in payload.items:
            product = products[item.product_id]
            unit_price = product.price
            line_total = unit_price * item.quantity
            total_amount += line_total
            normalized_items.append(
                OrderItemPricedCreate(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=unit_price,
                    line_total=line_total,
                )
            )

        for product_id, requested_quantity in requested_quantities.items():
            products[product_id].stock_quantity -= requested_quantity

        normalized_payload = OrderPricedCreate(
            customer_id=payload.customer_id,
            order_date=payload.order_date,
            total_amount=total_amount,
            status=payload.status,
            items=normalized_items,
        )
        return self.order_repository.create_order(normalized_payload)

    def get_by_id(self, order_id: int) -> Order:
        return self.order_repository.get_by_id(order_id)

    def list(
        self,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
    ) -> tuple[list[Order], int]:
        return self.order_repository.list(
            page=page,
            page_size=page_size,
            status=status,
        )

    def update_status(self, order_id: int, status: str) -> Order:
        if not status.strip():
            raise DomainValidationError("Order status cannot be empty")
        return self.order_repository.update_status(order_id, status)

    def update(self, order_id: int, payload: OrderUpdate) -> Order:
        return self.order_repository.update(order_id, payload)

    def delete(self, order_id: int) -> None:
        self.order_repository.delete(order_id)
