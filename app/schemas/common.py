"""Shared Pydantic schema types."""

from pydantic import BaseModel, ConfigDict, Field


class OrmSchema(BaseModel):
    """Base schema configured for ORM serialization."""

    model_config = ConfigDict(from_attributes=True)


class PaginationParams(BaseModel):
    """Reusable pagination request parameters."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
