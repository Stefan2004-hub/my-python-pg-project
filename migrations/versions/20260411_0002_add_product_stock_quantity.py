"""Add product stock quantity.

Revision ID: 20260411_0002
Revises: 20260411_0001
Create Date: 2026-04-11 00:02:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260411_0002"
down_revision: str | None = "20260411_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "products",
        sa.Column(
            "stock_quantity",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
    )
    op.create_check_constraint(
        "ck_products_stock_quantity_non_negative",
        "products",
        "stock_quantity >= 0",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_products_stock_quantity_non_negative",
        "products",
        type_="check",
    )
    op.drop_column("products", "stock_quantity")
