"""API route modules."""

from app.api.routes.categories import router as categories_router
from app.api.routes.customers import router as customers_router
from app.api.routes.orders import router as orders_router
from app.api.routes.products import router as products_router
from app.api.routes.reports import router as reports_router

__all__ = [
    "categories_router",
    "customers_router",
    "orders_router",
    "products_router",
    "reports_router",
]
