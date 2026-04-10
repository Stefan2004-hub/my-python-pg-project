"""Repository for order persistence."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import DomainValidationError, NotFoundError
from app.models import Customer, Order, OrderItem, Product
from app.schemas.order import OrderPricedCreate, OrderUpdate


class OrderRepository:
    """Data-access logic for orders and order items."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_order(self, payload: OrderPricedCreate) -> Order:
        customer = self.db.get(Customer, payload.customer_id)
        if customer is None:
            raise NotFoundError("Customer not found")

        product_ids = [item.product_id for item in payload.items]
        if not product_ids:
            raise DomainValidationError("Order must include at least one item")

        products = {
            product.id: product
            for product in self.db.scalars(
                select(Product).where(Product.id.in_(product_ids))
            )
        }
        missing_product_ids = sorted(set(product_ids) - set(products))
        if missing_product_ids:
            raise NotFoundError(
                f"Products not found: {', '.join(str(product_id) for product_id in missing_product_ids)}"
            )

        order_data = payload.model_dump(exclude={"items"})
        order = Order(**order_data)
        self.db.add(order)
        self.db.flush()

        for item_payload in payload.items:
            product = products[item_payload.product_id]
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item_payload.quantity,
                unit_price=item_payload.unit_price,
                line_total=item_payload.line_total,
            )
            self.db.add(order_item)

        self.db.commit()
        return self.get_by_id(order.id)

    def get_by_id(self, order_id: int) -> Order:
        stmt = (
            select(Order)
            .options(
                selectinload(Order.customer),
                selectinload(Order.order_items).selectinload(OrderItem.product),
            )
            .where(Order.id == order_id)
        )
        order = self.db.scalar(stmt)
        if order is None:
            raise NotFoundError("Order not found")
        return order

    def list(
        self,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
    ) -> tuple[list[Order], int]:
        offset = (page - 1) * page_size
        base_stmt = select(Order)
        count_stmt = select(func.count()).select_from(Order)
        if status:
            base_stmt = base_stmt.where(Order.status == status)
            count_stmt = count_stmt.where(Order.status == status)

        total = self.db.scalar(count_stmt) or 0
        items = list(
            self.db.scalars(
                base_stmt
                .options(
                    selectinload(Order.customer),
                    selectinload(Order.order_items).selectinload(OrderItem.product),
                )
                .order_by(Order.id)
                .offset(offset)
                .limit(page_size)
            )
        )
        return items, total

    def update_status(self, order_id: int, status: str) -> Order:
        order = self.get_by_id(order_id)
        order.status = status
        self.db.commit()
        self.db.refresh(order)
        return self.get_by_id(order.id)

    def update(self, order_id: int, payload: OrderUpdate) -> Order:
        order = self.get_by_id(order_id)
        update_data = payload.model_dump(exclude_none=True, exclude={"items"})
        for field, value in update_data.items():
            setattr(order, field, value)
        self.db.commit()
        return self.get_by_id(order.id)

    def delete(self, order_id: int) -> None:
        order = self.get_by_id(order_id)
        self.db.delete(order)
        self.db.commit()
