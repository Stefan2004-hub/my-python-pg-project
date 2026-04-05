"""Repository for customer persistence."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerRepository:
    """Data-access logic for customers."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: CustomerCreate) -> Customer:
        customer = Customer(**payload.model_dump())
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def get_by_id(self, customer_id: int) -> Customer:
        customer = self.db.get(Customer, customer_id)
        if customer is None:
            raise NotFoundError("Customer not found")
        return customer

    def get_by_email(self, email: str) -> Customer | None:
        return self.db.scalar(select(Customer).where(Customer.email == email))

    def list(self, page: int = 1, page_size: int = 20) -> tuple[list[Customer], int]:
        offset = (page - 1) * page_size
        total = self.db.scalar(select(func.count()).select_from(Customer)) or 0
        items = list(
            self.db.scalars(
                select(Customer)
                .order_by(Customer.id)
                .offset(offset)
                .limit(page_size)
            )
        )
        return items, total

    def update(self, customer_id: int, payload: CustomerUpdate) -> Customer:
        customer = self.get_by_id(customer_id)
        for field, value in payload.model_dump(exclude_none=True).items():
            setattr(customer, field, value)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def delete(self, customer_id: int) -> None:
        customer = self.get_by_id(customer_id)
        self.db.delete(customer)
        self.db.commit()
