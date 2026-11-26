from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.modules.credit_scoring.models.application import CreditApplication


class ApplicationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        *,
        customer_id: UUID,
        requested_amount,
        currency_code: str,
        term_months: int,
        purpose: str,
    ) -> CreditApplication:
        application = CreditApplication(
            customer_id=customer_id,
            requested_amount=requested_amount,
            currency_code=currency_code,
            term_months=term_months,
            purpose=purpose,
        )

        self.session.add(application)
        self.session.flush()

        return application

    def get_by_id(
        self,
        application_id: UUID,
    ) -> CreditApplication | None:
        statement = (
            select(CreditApplication)
            .options(joinedload(CreditApplication.customer))
            .where(CreditApplication.id == application_id)
        )

        return self.session.scalar(statement)

    def list_by_customer(
        self,
        customer_id: UUID,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[CreditApplication]:
        statement = (
            select(CreditApplication)
            .where(CreditApplication.customer_id == customer_id)
            .order_by(CreditApplication.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        return list(self.session.scalars(statement).all())

    def list_all(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> list[CreditApplication]:
        statement = (
            select(CreditApplication)
            .order_by(CreditApplication.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        return list(self.session.scalars(statement).all())

    def update_status(
        self,
        application: CreditApplication,
        status: str,
    ) -> CreditApplication:
        application.status = status
        self.session.flush()

        return application
