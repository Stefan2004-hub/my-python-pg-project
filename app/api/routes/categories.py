"""Category API routes."""

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.services import CategoryService


router = APIRouter(prefix="/categories", tags=["categories"])


class CategoryPage(BaseModel):
    """Paginated category response."""

    items: list[CategoryRead]
    total: int
    page: int
    page_size: int


def get_category_service(db: Session = Depends(get_db)) -> CategoryService:
    return CategoryService(db)


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    service: CategoryService = Depends(get_category_service),
):
    return service.create(payload)


@router.get("", response_model=CategoryPage)
def list_categories(
    page: int = 1,
    page_size: int = 20,
    service: CategoryService = Depends(get_category_service),
):
    items, total = service.list(page=page, page_size=page_size)
    return CategoryPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{category_id}", response_model=CategoryRead)
def get_category(
    category_id: int,
    service: CategoryService = Depends(get_category_service),
):
    return service.get_by_id(category_id)


@router.put("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    service: CategoryService = Depends(get_category_service),
):
    return service.update(category_id, payload)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    service: CategoryService = Depends(get_category_service),
):
    service.delete(category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
