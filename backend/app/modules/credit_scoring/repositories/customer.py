from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.credit_scoring.models.customer import Customer


class CustomerRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        *,
        full_name: str,
        date_of_birth=None,
        email: str | None = None,
        monthly_income: Decimal | None = None,
        monthly_debt_payments: Decimal | None = None,
        employment_months: int | None = None,
        employment_status: str | None = None,
    ) -> Customer:
        customer = Customer(
            full_name=full_name,
            date_of_birth=date_of_birth,
            email=email,
            monthly_income=monthly_income,
            monthly_debt_payments=monthly_debt_payments,
            employment_months=employment_months,
            employment_status=employment_status,
        )

        self.session.add(customer)
        self.session.flush()

        return customer

    def get_by_id(self, customer_id: UUID) -> Customer | None:
        statement = select(Customer).where(Customer.id == customer_id)
        return self.session.scalar(statement)

    def get_by_email(self, email: str) -> Customer | None:
        statement = select(Customer).where(Customer.email == email)
        return self.session.scalar(statement)

    def list(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Customer]:
        statement = (
            select(Customer)
            .order_by(Customer.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        return list(self.session.scalars(statement).all())

    def update(
        self,
        customer: Customer,
        **data: object,
    ) -> Customer:
        for field, value in data.items():
            setattr(customer, field, value)

        self.session.flush()
        return customer
