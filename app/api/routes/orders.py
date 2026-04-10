"""Order API routes."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.order import OrderCreate, OrderItemCreate, OrderRead, OrderUpdate
from app.services import OrderService


router = APIRouter(prefix="/orders", tags=["orders"])


class OrderItemCreateRequest(BaseModel):
    """Public order item create payload."""

    model_config = ConfigDict(extra="forbid")

    product_id: int
    quantity: int = Field(gt=0)


class OrderCreateRequest(BaseModel):
    """Public order create payload."""

    model_config = ConfigDict(extra="forbid")

    customer_id: int
    order_date: datetime | None = None
    status: str = "pending"
    items: list[OrderItemCreateRequest]


class OrderStatusUpdate(BaseModel):
    """Order status update payload."""

    status: str


class OrderPage(BaseModel):
    """Paginated order response."""

    items: list[OrderRead]
    total: int
    page: int
    page_size: int


def get_order_service(db: Session = Depends(get_db)) -> OrderService:
    return OrderService(db)


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreateRequest,
    service: Annotated[OrderService, Depends(get_order_service)],
):
    service_payload = OrderCreate(
        customer_id=payload.customer_id,
        order_date=payload.order_date,
        status=payload.status,
        items=[
            OrderItemCreate(
                product_id=item.product_id,
                quantity=item.quantity,
            )
            for item in payload.items
        ],
    )
    return service.create_order(service_payload)


@router.get("", response_model=OrderPage)
def list_orders(
    service: Annotated[OrderService, Depends(get_order_service)],
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
):
    items, total = service.list(page=page, page_size=page_size, status=status)
    return OrderPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{order_id}", response_model=OrderRead)
def get_order(
    order_id: int,
    service: Annotated[OrderService, Depends(get_order_service)],
):
    return service.get_by_id(order_id)


@router.patch("/{order_id}/status", response_model=OrderRead)
def update_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    service: Annotated[OrderService, Depends(get_order_service)],
):
    return service.update_status(order_id, payload.status)


@router.put("/{order_id}", response_model=OrderRead)
def update_order(
    order_id: int,
    payload: OrderUpdate,
    service: Annotated[OrderService, Depends(get_order_service)],
):
    return service.update(order_id, payload)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(
    order_id: int,
    service: Annotated[OrderService, Depends(get_order_service)],
):
    service.delete(order_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
