from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.modules.credit_scoring.models.assessment import CreditAssessment
    from app.modules.credit_scoring.models.customer import Customer
    from app.modules.credit_scoring.models.decision import CreditDecision


class CreditApplication(Base):
    __tablename__ = "credit_applications"

    __table_args__ = (
        CheckConstraint(
            "requested_amount > 0",
            name="ck_credit_applications_amount_positive",
        ),
        CheckConstraint(
            "term_months > 0",
            name="ck_credit_applications_term_positive",
        ),
        CheckConstraint(
            "status IN ('pending', 'assessed', 'approved', 'rejected', 'withdrawn')",
            name="ck_credit_applications_status",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    customer_id: Mapped[UUID] = mapped_column(
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    requested_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    term_months: Mapped[int] = mapped_column(nullable=False)
    purpose: Mapped[str] = mapped_column(String(100), nullable=False)

    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", server_default="pending"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    customer: Mapped["Customer"] = relationship(back_populates="applications")
    assessments: Mapped[list["CreditAssessment"]] = relationship(
        back_populates="application"
    )
    decisions: Mapped[list["CreditDecision"]] = relationship(
        back_populates="application"
    )
