"""Repository for product persistence."""

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import NotFoundError
from app.models import Product
from app.schemas.product import ProductCreate, ProductUpdate


class ProductRepository:
    """Data-access logic for products."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: ProductCreate) -> Product:
        product = Product(**payload.model_dump())
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def get_by_id(self, product_id: int) -> Product:
        stmt = (
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.id == product_id)
        )
        product = self.db.scalar(stmt)
        if product is None:
            raise NotFoundError("Product not found")
        return product

    def list(
        self,
        page: int = 1,
        page_size: int = 20,
        category_id: int | None = None,
        search: str | None = None,
    ) -> tuple[list[Product], int]:
        offset = (page - 1) * page_size
        filters = []
        if category_id is not None:
            filters.append(Product.category_id == category_id)
        if search:
            pattern = f"%{search.strip()}%"
            filters.append(
                or_(
                    Product.name.ilike(pattern),
                    Product.description.ilike(pattern),
                )
            )

        base_stmt = select(Product)
        count_stmt = select(func.count()).select_from(Product)
        if filters:
            base_stmt = base_stmt.where(*filters)
            count_stmt = count_stmt.where(*filters)

        total = self.db.scalar(count_stmt) or 0
        items = list(
            self.db.scalars(
                base_stmt
                .options(selectinload(Product.category))
                .order_by(Product.id)
                .offset(offset)
                .limit(page_size)
            )
        )
        return items, total

    def update(self, product_id: int, payload: ProductUpdate) -> Product:
        product = self.get_by_id(product_id)
        for field, value in payload.model_dump(exclude_none=True).items():
            setattr(product, field, value)
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product_id: int) -> None:
        product = self.get_by_id(product_id)
        self.db.delete(product)
        self.db.commit()
