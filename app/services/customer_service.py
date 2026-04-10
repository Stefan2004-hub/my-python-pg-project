"""Business logic for customers."""

from sqlalchemy.orm import Session

from app.core.exceptions import DomainValidationError
from app.models import Customer
from app.repositories import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerService:
    """Service API for customer use cases."""

    def __init__(self, db: Session) -> None:
        self.repository = CustomerRepository(db)

    def create(self, payload: CustomerCreate) -> Customer:
        if self.repository.get_by_email(payload.email) is not None:
            raise DomainValidationError("Customer email already exists")
        return self.repository.create(payload)

    def get_by_id(self, customer_id: int) -> Customer:
        return self.repository.get_by_id(customer_id)

    def list(self, page: int = 1, page_size: int = 20) -> tuple[list[Customer], int]:
        return self.repository.list(page=page, page_size=page_size)

    def update(self, customer_id: int, payload: CustomerUpdate) -> Customer:
        return self.repository.update(customer_id, payload)

    def delete(self, customer_id: int) -> None:
        self.repository.delete(customer_id)
