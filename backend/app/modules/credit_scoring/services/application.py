from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.credit_scoring.models.application import CreditApplication
from app.modules.credit_scoring.repositories.application import (
    ApplicationRepository,
)
from app.modules.credit_scoring.repositories.customer import CustomerRepository
from app.modules.credit_scoring.schemas.application import ApplicationCreate


class ApplicationService:
    def __init__(self, session: Session) -> None:
        self.repository = ApplicationRepository(session)
        self.customer_repository = CustomerRepository(session)

    def create_application(
        self,
        data: ApplicationCreate,
    ) -> CreditApplication:
        customer = self.customer_repository.get_by_id(data.customer_id)

        if customer is None:
            raise ValueError("Customer not found")

        return self.repository.create(
            customer_id=data.customer_id,
            requested_amount=data.requested_amount,
            currency_code=data.currency_code,
            term_months=data.term_months,
            purpose=data.purpose,
        )

    def get_application(
        self,
        application_id: UUID,
    ) -> CreditApplication | None:
        return self.repository.get_by_id(application_id)

    def get_customer_applications(
        self,
        customer_id: UUID,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[CreditApplication]:
        if offset < 0:
            raise ValueError("Offset cannot be negative")

        if not 1 <= limit <= 100:
            raise ValueError("Limit must be between 1 and 100")

        customer = self.customer_repository.get_by_id(customer_id)

        if customer is None:
            raise ValueError("Customer not found")

        return self.repository.list_by_customer(
            customer_id,
            offset=offset,
            limit=limit,
        )

    def get_all_applications(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> list[CreditApplication]:
        if offset < 0:
            raise ValueError("Offset cannot be negative")

        if not 1 <= limit <= 100:
            raise ValueError("Limit must be between 1 and 100")

        return self.repository.list_all(
            offset=offset,
            limit=limit,
        )
