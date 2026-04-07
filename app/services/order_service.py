"""Business logic for orders."""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import DomainValidationError
from app.models import Order
from app.repositories import OrderRepository, ProductRepository
from app.schemas.order import OrderCreate, OrderItemCreate, OrderUpdate


class OrderService:
    """Service API for order use cases."""

    def __init__(self, db: Session) -> None:
        self.order_repository = OrderRepository(db)
        self.product_repository = ProductRepository(db)

    def create_order(self, payload: OrderCreate) -> Order:
        if not payload.items:
            raise DomainValidationError("Order must include at least one item")

        normalized_items: list[OrderItemCreate] = []
        total_amount = Decimal("0.00")
        for item in payload.items:
            if item.quantity <= 0:
                raise DomainValidationError("Order item quantity must be positive")

            product = self.product_repository.get_by_id(item.product_id)
            unit_price = product.price
            line_total = unit_price * item.quantity
            total_amount += line_total
            normalized_items.append(
                OrderItemCreate(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=unit_price,
                    line_total=line_total,
                )
            )

        normalized_payload = OrderCreate(
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
