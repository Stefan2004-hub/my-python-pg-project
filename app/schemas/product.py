"""Product schemas."""

from decimal import Decimal

from app.schemas.common import OrmSchema


class ProductBase(OrmSchema):
    """Shared product fields."""

    name: str
    description: str | None = None
    price: Decimal
    category_id: int | None = None


class ProductCreate(ProductBase):
    """Payload for creating a product."""


class ProductUpdate(OrmSchema):
    """Payload for updating a product."""

    name: str | None = None
    description: str | None = None
    price: Decimal | None = None
    category_id: int | None = None


class ProductRead(ProductBase):
    """Product response payload."""

    id: int
