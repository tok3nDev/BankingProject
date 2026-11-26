from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.modules.credit_scoring.models.application import CreditApplication
    from app.modules.credit_scoring.models.assessment import CreditAssessment


class CreditDecision(Base):
    __tablename__ = "credit_decisions"

    __table_args__ = (
        CheckConstraint(
            "decision_status IN ('approved', 'rejected', 'manual_review')",
            name="ck_credit_decisions_status",
        ),
        ForeignKeyConstraint(
            ["assessment_id", "application_id"],
            [
                "credit_assessments.id",
                "credit_assessments.application_id",
            ],
            name="fk_credit_decisions_assessment_application",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    application_id: Mapped[UUID] = mapped_column(
        ForeignKey("credit_applications.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    assessment_id: Mapped[UUID | None] = mapped_column(
        nullable=True,
    )

    decision_status: Mapped[str] = mapped_column(String(20), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    decided_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    application: Mapped["CreditApplication"] = relationship(back_populates="decisions")
    assessment: Mapped["CreditAssessment | None"] = relationship(
        back_populates="decisions"
    )
