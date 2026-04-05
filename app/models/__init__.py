"""ORM models package."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all ORM models."""


from app.models.category import Category
from app.models.customer import Customer
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product

__all__ = [
    "Base",
    "Category",
    "Customer",
    "Order",
    "OrderItem",
    "Product",
]
