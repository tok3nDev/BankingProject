from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.credit_scoring.models.assessment import CreditAssessment
from app.modules.credit_scoring.repositories.application import (
    ApplicationRepository,
)
from app.modules.credit_scoring.repositories.assessment import (
    AssessmentRepository,
)


class AssessmentService:
    def __init__(self, session: Session) -> None:
        self.repository = AssessmentRepository(session)
        self.application_repository = ApplicationRepository(session)

    def create_assessment(
        self,
        *,
        application_id: UUID,
        probability_of_default,
        credit_score: int,
        model_name: str,
        model_version: str,
        features: dict,
    ) -> CreditAssessment:
        application = self.application_repository.get_by_id(application_id)

        if application is None:
            raise ValueError("Credit application not found")

        assessment = self.repository.create(
            application_id=application_id,
            probability_of_default=probability_of_default,
            credit_score=credit_score,
            model_name=model_name,
            model_version=model_version,
            features=features,
        )

        self.application_repository.update_status(application, "assessed")

        return assessment

    def get_assessment(
        self,
        assessment_id: UUID,
    ) -> CreditAssessment | None:
        return self.repository.get_by_id(assessment_id)

    def get_application_assessments(
        self,
        application_id: UUID,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[CreditAssessment]:
        if offset < 0:
            raise ValueError("Offset cannot be negative")

        if not 1 <= limit <= 100:
            raise ValueError("Limit must be between 1 and 100")

        application = self.application_repository.get_by_id(application_id)

        if application is None:
            raise ValueError("Credit application not found")

        return self.repository.list_by_application(
            application_id,
            offset=offset,
            limit=limit,
        )
