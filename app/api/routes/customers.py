"""Customer API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.customer import CustomerCreate, CustomerRead, CustomerUpdate
from app.services import CustomerService


router = APIRouter(prefix="/customers", tags=["customers"])


class CustomerPage(BaseModel):
    """Paginated customer response."""

    items: list[CustomerRead]
    total: int
    page: int
    page_size: int


def get_customer_service(db: Session = Depends(get_db)) -> CustomerService:
    return CustomerService(db)


@router.post("", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
def create_customer(
    payload: CustomerCreate,
    service: Annotated[CustomerService, Depends(get_customer_service)],
):
    return service.create(payload)


@router.get("", response_model=CustomerPage)
def list_customers(
    service: Annotated[CustomerService, Depends(get_customer_service)],
    page: int = 1,
    page_size: int = 20,
):
    items, total = service.list(page=page, page_size=page_size)
    return CustomerPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer(
    customer_id: int,
    service: Annotated[CustomerService, Depends(get_customer_service)],
):
    return service.get_by_id(customer_id)


@router.put("/{customer_id}", response_model=CustomerRead)
def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    service: Annotated[CustomerService, Depends(get_customer_service)],
):
    return service.update(customer_id, payload)


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    customer_id: int,
    service: Annotated[CustomerService, Depends(get_customer_service)],
):
    service.delete(customer_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
