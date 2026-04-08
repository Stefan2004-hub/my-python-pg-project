"""Product API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate
from app.services import ProductService


router = APIRouter(prefix="/products", tags=["products"])


class ProductPage(BaseModel):
    """Paginated product response."""

    items: list[ProductRead]
    total: int
    page: int
    page_size: int


def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(db)


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    service: Annotated[ProductService, Depends(get_product_service)],
):
    return service.create(payload)


@router.get("", response_model=ProductPage)
def list_products(
    service: Annotated[ProductService, Depends(get_product_service)],
    page: int = 1,
    page_size: int = 20,
    category_id: int | None = None,
    search: str | None = None,
):
    items, total = service.list(
        page=page,
        page_size=page_size,
        category_id=category_id,
        search=search,
    )
    return ProductPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{product_id}", response_model=ProductRead)
def get_product(
    product_id: int,
    service: Annotated[ProductService, Depends(get_product_service)],
):
    return service.get_by_id(product_id)


@router.put("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    service: Annotated[ProductService, Depends(get_product_service)],
):
    return service.update(product_id, payload)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    service: Annotated[ProductService, Depends(get_product_service)],
):
    service.delete(product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
