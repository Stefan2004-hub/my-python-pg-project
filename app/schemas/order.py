"""Order and order-item schemas."""

from datetime import datetime
from decimal import Decimal

from app.schemas.common import OrmSchema


class OrderItemBase(OrmSchema):
    """Shared order item fields."""

    product_id: int
    quantity: int
    unit_price: Decimal
    line_total: Decimal


class OrderItemCreate(OrderItemBase):
    """Payload for creating an order item."""


class OrderItemUpdate(OrmSchema):
    """Payload for updating an order item."""

    product_id: int | None = None
    quantity: int | None = None
    unit_price: Decimal | None = None
    line_total: Decimal | None = None


class OrderItemRead(OrderItemBase):
    """Order item response payload."""

    id: int
    order_id: int


class OrderBase(OrmSchema):
    """Shared order fields."""

    customer_id: int
    order_date: datetime | None = None
    total_amount: Decimal
    status: str


class OrderCreate(OrderBase):
    """Payload for creating an order."""

    items: list[OrderItemCreate]


class OrderUpdate(OrmSchema):
    """Payload for updating an order."""

    customer_id: int | None = None
    order_date: datetime | None = None
    total_amount: Decimal | None = None
    status: str | None = None
    items: list[OrderItemUpdate] | None = None


class OrderRead(OrderBase):
    """Order response payload."""

    id: int
    items: list[OrderItemRead]
