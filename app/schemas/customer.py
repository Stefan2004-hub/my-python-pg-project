"""Customer schemas."""

from app.schemas.common import OrmSchema


class CustomerBase(OrmSchema):
    """Shared customer fields."""

    first_name: str
    last_name: str
    email: str
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None


class CustomerCreate(CustomerBase):
    """Payload for creating a customer."""


class CustomerUpdate(OrmSchema):
    """Payload for updating a customer."""

    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None


class CustomerRead(CustomerBase):
    """Customer response payload."""

    id: int
