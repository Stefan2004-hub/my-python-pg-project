"""Repository for category persistence."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryRepository:
    """Data-access logic for categories."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: CategoryCreate) -> Category:
        category = Category(**payload.model_dump())
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def get_by_id(self, category_id: int) -> Category:
        category = self.db.get(Category, category_id)
        if category is None:
            raise NotFoundError("Category not found")
        return category

    def list(self, page: int = 1, page_size: int = 20) -> tuple[list[Category], int]:
        offset = (page - 1) * page_size
        total = self.db.scalar(select(func.count()).select_from(Category)) or 0
        items = list(
            self.db.scalars(
                select(Category)
                .order_by(Category.id)
                .offset(offset)
                .limit(page_size)
            )
        )
        return items, total

    def update(self, category_id: int, payload: CategoryUpdate) -> Category:
        category = self.get_by_id(category_id)
        for field, value in payload.model_dump(exclude_none=True).items():
            setattr(category, field, value)
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete(self, category_id: int) -> None:
        category = self.get_by_id(category_id)
        self.db.delete(category)
        self.db.commit()
