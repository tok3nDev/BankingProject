from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.credit_scoring.models.assessment import CreditAssessment


class AssessmentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        *,
        application_id: UUID,
        probability_of_default: Decimal,
        credit_score: int,
        model_name: str,
        model_version: str,
        features: dict[str, object],
    ) -> CreditAssessment:
        assessment = CreditAssessment(
            application_id=application_id,
            probability_of_default=probability_of_default,
            credit_score=credit_score,
            model_name=model_name,
            model_version=model_version,
            features=features,
        )

        self.session.add(assessment)
        self.session.flush()

        return assessment

    def get_by_id(
        self,
        assessment_id: UUID,
    ) -> CreditAssessment | None:
        statement = select(CreditAssessment).where(CreditAssessment.id == assessment_id)
        return self.session.scalar(statement)

    def list_by_application(
        self,
        application_id: UUID,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[CreditAssessment]:
        statement = (
            select(CreditAssessment)
            .where(CreditAssessment.application_id == application_id)
            .order_by(CreditAssessment.evaluated_at.desc())
            .offset(offset)
            .limit(limit)
        )

        return list(self.session.scalars(statement).all())
