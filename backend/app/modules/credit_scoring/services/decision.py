from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.credit_scoring.models.decision import CreditDecision
from app.modules.credit_scoring.repositories.application import (
    ApplicationRepository,
)
from app.modules.credit_scoring.repositories.assessment import (
    AssessmentRepository,
)
from app.modules.credit_scoring.repositories.decision import DecisionRepository


class DecisionConflictError(Exception):
    pass


class DecisionService:
    def __init__(self, session: Session) -> None:
        self.repository = DecisionRepository(session)
        self.application_repository = ApplicationRepository(session)
        self.assessment_repository = AssessmentRepository(session)

    def create_decision(
        self,
        *,
        application_id: UUID,
        decision_status: str,
        assessment_id: UUID | None = None,
        reason: str | None = None,
    ) -> CreditDecision:
        application = self.application_repository.get_by_id(application_id)

        if application is None:
            raise ValueError("Credit application not found")

        has_final_decision = self.repository.has_final_decision(application_id)

        if has_final_decision:
            raise DecisionConflictError(
                "A final decision already exists for this application"
            )

        if assessment_id is not None:
            assessment = self.assessment_repository.get_by_id(assessment_id)

            if assessment is None:
                raise ValueError("Credit assessment not found")

            if assessment.application_id != application_id:
                raise ValueError("Assessment does not belong to this application")

        decision = self.repository.create(
            application_id=application_id,
            assessment_id=assessment_id,
            decision_status=decision_status,
            reason=reason,
        )

        if decision_status in {"approved", "rejected"}:
            self.application_repository.update_status(
                application,
                decision_status,
            )

        return decision

    def get_decision(self, decision_id: UUID) -> CreditDecision | None:
        return self.repository.get_by_id(decision_id)

    def get_application_decisions(
        self,
        application_id: UUID,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[CreditDecision]:
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
