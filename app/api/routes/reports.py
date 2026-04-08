"""Reporting API routes."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services import ReportService


router = APIRouter(prefix="/reports", tags=["reports"])


def get_report_service(db: Session = Depends(get_db)) -> ReportService:
    return ReportService(db)


@router.get("/sales-by-product")
def sales_by_product(
    service: Annotated[ReportService, Depends(get_report_service)],
) -> list[dict[str, Any]]:
    return service.sales_by_product()


@router.get("/sales-by-category")
def sales_by_category(
    service: Annotated[ReportService, Depends(get_report_service)],
) -> list[dict[str, Any]]:
    return service.sales_by_category()


@router.get("/top-products")
def top_products(
    service: Annotated[ReportService, Depends(get_report_service)], limit: int = 10
) -> list[dict[str, Any]]:
    return service.top_products(limit=limit)


@router.get("/daily-sales")
def daily_sales(
    service: Annotated[ReportService, Depends(get_report_service)],
) -> list[dict[str, Any]]:
    return service.daily_sales()


@router.get("/customers/{customer_id}/orders")
def customer_order_history(
    customer_id: int,
    service: Annotated[ReportService, Depends(get_report_service)],
) -> list[dict[str, Any]]:
    return service.customer_order_history(customer_id)
