"""Business logic for products."""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import DomainValidationError
from app.models import Product
from app.repositories import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate


class ProductService:
    """Service API for product use cases."""

    def __init__(self, db: Session) -> None:
        self.repository = ProductRepository(db)

    def create(self, payload: ProductCreate) -> Product:
        self._validate_price(payload.price)
        return self.repository.create(payload)

    def get_by_id(self, product_id: int) -> Product:
        return self.repository.get_by_id(product_id)

    def list(
        self,
        page: int = 1,
        page_size: int = 20,
        category_id: int | None = None,
        search: str | None = None,
    ) -> tuple[list[Product], int]:
        return self.repository.list(
            page=page,
            page_size=page_size,
            category_id=category_id,
            search=search,
        )

    def update(self, product_id: int, payload: ProductUpdate) -> Product:
        if payload.price is not None:
            self._validate_price(payload.price)
        return self.repository.update(product_id, payload)

    def delete(self, product_id: int) -> None:
        self.repository.delete(product_id)

    @staticmethod
    def _validate_price(price: Decimal) -> None:
        if price < 0:
            raise DomainValidationError("Product price cannot be negative")
