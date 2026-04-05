"""Category schemas."""

from app.schemas.common import OrmSchema


class CategoryBase(OrmSchema):
    """Shared category fields."""

    name: str
    description: str | None = None


class CategoryCreate(CategoryBase):
    """Payload for creating a category."""


class CategoryUpdate(OrmSchema):
    """Payload for updating a category."""

    name: str | None = None
    description: str | None = None


class CategoryRead(CategoryBase):
    """Category response payload."""

    id: int
