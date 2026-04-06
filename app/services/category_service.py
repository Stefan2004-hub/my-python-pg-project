"""Business logic for categories."""

from sqlalchemy.orm import Session

from app.models import Category
from app.repositories import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    """Service API for category use cases."""

    def __init__(self, db: Session) -> None:
        self.repository = CategoryRepository(db)

    def create(self, payload: CategoryCreate) -> Category:
        return self.repository.create(payload)

    def get_by_id(self, category_id: int) -> Category:
        return self.repository.get_by_id(category_id)

    def list(self, page: int = 1, page_size: int = 20) -> tuple[list[Category], int]:
        return self.repository.list(page=page, page_size=page_size)

    def update(self, category_id: int, payload: CategoryUpdate) -> Category:
        return self.repository.update(category_id, payload)

    def delete(self, category_id: int) -> None:
        self.repository.delete(category_id)
