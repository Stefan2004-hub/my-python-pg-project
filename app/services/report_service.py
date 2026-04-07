"""Pandas-backed reporting services."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any

import pandas as pd
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Category, Customer, Order, OrderItem, Product


class ReportService:
    """Read-only analytics service backed by SQLAlchemy and Pandas."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def sales_by_product(self) -> list[dict[str, Any]]:
        rows = self.db.execute(
            select(
                Product.id.label("product_id"),
                Product.name.label("product_name"),
                func.sum(OrderItem.quantity).label("quantity_sold"),
                func.sum(OrderItem.line_total).label("total_sales"),
            )
            .join(OrderItem, OrderItem.product_id == Product.id)
            .group_by(Product.id, Product.name)
            .order_by(Product.id)
        ).mappings()
        return self._records(pd.DataFrame(rows))

    def sales_by_category(self) -> list[dict[str, Any]]:
        rows = self.db.execute(
            select(
                Category.id.label("category_id"),
                Category.name.label("category_name"),
                func.sum(OrderItem.quantity).label("quantity_sold"),
                func.sum(OrderItem.line_total).label("total_sales"),
            )
            .join(Product, Product.category_id == Category.id)
            .join(OrderItem, OrderItem.product_id == Product.id)
            .group_by(Category.id, Category.name)
            .order_by(Category.id)
        ).mappings()
        return self._records(pd.DataFrame(rows))

    def top_products(self, limit: int = 10) -> list[dict[str, Any]]:
        rows = self.db.execute(
            select(
                Product.id.label("product_id"),
                Product.name.label("product_name"),
                func.sum(OrderItem.quantity).label("quantity_sold"),
                func.sum(OrderItem.line_total).label("total_sales"),
            )
            .join(OrderItem, OrderItem.product_id == Product.id)
            .group_by(Product.id, Product.name)
            .order_by(func.sum(OrderItem.quantity).desc(), Product.id)
            .limit(limit)
        ).mappings()
        return self._records(pd.DataFrame(rows))

    def daily_sales(self) -> list[dict[str, Any]]:
        order_day = func.date(Order.order_date)
        rows = self.db.execute(
            select(
                order_day.label("order_date"),
                func.count(Order.id).label("order_count"),
                func.sum(Order.total_amount).label("total_sales"),
            )
            .group_by(order_day)
            .order_by(order_day)
        ).mappings()
        return self._records(pd.DataFrame(rows))

    def customer_order_history(self, customer_id: int) -> list[dict[str, Any]]:
        rows = self.db.execute(
            select(
                Customer.id.label("customer_id"),
                Customer.email.label("customer_email"),
                Order.id.label("order_id"),
                Order.order_date.label("order_date"),
                Order.status.label("status"),
                Order.total_amount.label("total_amount"),
            )
            .join(Order, Order.customer_id == Customer.id)
            .where(Customer.id == customer_id)
            .order_by(Order.order_date, Order.id)
        ).mappings()
        return self._records(pd.DataFrame(rows))

    def _records(self, df: pd.DataFrame) -> list[dict[str, Any]]:
        if df.empty:
            return []
        return [
            {key: self._json_safe(value) for key, value in row.items()}
            for row in df.to_dict(orient="records")
        ]

    def _json_safe(self, value: Any) -> Any:
        if value is None or pd.isna(value):
            return None
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, datetime | date):
            return value.isoformat()
        if hasattr(value, "item"):
            return value.item()
        return value
