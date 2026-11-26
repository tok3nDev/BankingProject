from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.modules.credit_scoring.models.application import CreditApplication
    from app.modules.credit_scoring.models.decision import CreditDecision


class CreditAssessment(Base):
    __tablename__ = "credit_assessments"

    __table_args__ = (
        CheckConstraint(
            "probability_of_default >= 0 AND probability_of_default <= 1",
            name="ck_credit_assessments_pd_range",
        ),
        CheckConstraint(
            "credit_score >= 0 AND credit_score <= 1000",
            name="ck_credit_assessments_score_range",
        ),
        UniqueConstraint(
            "id",
            "application_id",
            name="uq_credit_assessments_id_application",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    application_id: Mapped[UUID] = mapped_column(
        ForeignKey("credit_applications.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    probability_of_default: Mapped[Decimal] = mapped_column(
        Numeric(7, 6), nullable=False
    )
    credit_score: Mapped[int] = mapped_column(Integer, nullable=False)

    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)

    features: Mapped[dict] = mapped_column(JSON, nullable=False)

    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    application: Mapped["CreditApplication"] = relationship(
        back_populates="assessments"
    )
    decisions: Mapped[list["CreditDecision"]] = relationship(
        back_populates="assessment"
    )
