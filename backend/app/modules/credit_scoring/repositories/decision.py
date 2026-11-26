from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from app.modules.credit_scoring.models.decision import CreditDecision


class DecisionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        *,
        application_id: UUID,
        decision_status: str,
        assessment_id: UUID | None = None,
        reason: str | None = None,
    ) -> CreditDecision:
        decision = CreditDecision(
            application_id=application_id,
            assessment_id=assessment_id,
            decision_status=decision_status,
            reason=reason,
        )

        self.session.add(decision)
        self.session.flush()

        return decision

    def get_by_id(self, decision_id: UUID) -> CreditDecision | None:
        statement = select(CreditDecision).where(CreditDecision.id == decision_id)
        return self.session.scalar(statement)

    def has_final_decision(self, application_id: UUID) -> bool:
        statement = select(
            exists().where(
                CreditDecision.application_id == application_id,
                CreditDecision.decision_status.in_(["approved", "rejected"]),
            )
        )

        return bool(self.session.scalar(statement))

    def list_by_application(
        self,
        application_id: UUID,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[CreditDecision]:
        statement = (
            select(CreditDecision)
            .where(CreditDecision.application_id == application_id)
            .order_by(CreditDecision.decided_at.desc())
            .offset(offset)
            .limit(limit)
        )

        return list(self.session.scalars(statement).all())
