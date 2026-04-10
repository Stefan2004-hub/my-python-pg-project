"""Order and order-item schemas."""

from datetime import datetime
from decimal import Decimal

from app.schemas.common import OrmSchema


class OrderItemBase(OrmSchema):
    """Shared order item fields."""

    product_id: int
    quantity: int


class OrderItemPricedBase(OrderItemBase):
    """Order item fields with server-calculated pricing."""

    unit_price: Decimal
    line_total: Decimal


class OrderItemCreate(OrderItemBase):
    """Payload for creating an order item."""


class OrderItemPricedCreate(OrderItemPricedBase):
    """Trusted payload for persisting an order item."""


class OrderItemUpdate(OrmSchema):
    """Payload for updating an order item."""

    product_id: int | None = None
    quantity: int | None = None
    unit_price: Decimal | None = None
    line_total: Decimal | None = None


class OrderItemRead(OrderItemPricedBase):
    """Order item response payload."""

    id: int
    order_id: int


class OrderBase(OrmSchema):
    """Shared order fields."""

    customer_id: int
    order_date: datetime | None = None
    total_amount: Decimal
    status: str


class OrderCreate(OrmSchema):
    """Payload for creating an order."""

    customer_id: int
    order_date: datetime | None = None
    status: str
    items: list[OrderItemCreate]


class OrderPricedCreate(OrderBase):
    """Trusted payload for persisting an order."""

    items: list[OrderItemPricedCreate]


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
