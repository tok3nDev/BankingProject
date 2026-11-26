from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.credit_scoring.models.customer import Customer
from app.modules.credit_scoring.repositories.customer import CustomerRepository
from app.modules.credit_scoring.schemas.customer import CustomerCreate


class CustomerService:
    def __init__(self, session: Session) -> None:
        self.repository = CustomerRepository(session)

    def create_customer(self, data: CustomerCreate) -> Customer:
        if data.email and self.repository.get_by_email(data.email):
            raise ValueError("Customer with this email already exists")

        return self.repository.create(
            full_name=data.full_name,
            date_of_birth=data.date_of_birth,
            email=str(data.email) if data.email else None,
        )

    def get_customer(self, customer_id: UUID) -> Customer | None:
        return self.repository.get_by_id(customer_id)

    def get_customers(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Customer]:
        if offset < 0:
            raise ValueError("Offset cannot be negative")

        if not 1 <= limit <= 100:
            raise ValueError("Limit must be between 1 and 100")

        return self.repository.list(offset=offset, limit=limit)
