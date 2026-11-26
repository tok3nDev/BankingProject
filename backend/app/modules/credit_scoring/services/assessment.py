from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.credit_scoring.models.assessment import CreditAssessment
from app.modules.credit_scoring.repositories.application import (
    ApplicationRepository,
)
from app.modules.credit_scoring.repositories.assessment import (
    AssessmentRepository,
)


class AssessmentConflictError(Exception):
    pass


class AssessmentService:
    FINAL_STATUSES = {"approved", "rejected", "withdrawn"}

    MODEL_NAME = "rule_based_demo"
    MODEL_VERSION = "1.0"

    def __init__(self, session: Session) -> None:
        self.repository = AssessmentRepository(session)
        self.application_repository = ApplicationRepository(session)

    def create_assessment(
        self,
        *,
        application_id: UUID,
        probability_of_default: Decimal,
        credit_score: int,
        model_name: str,
        model_version: str,
        features: dict[str, object],
    ) -> CreditAssessment:
        application = self.application_repository.get_by_id(application_id)

        if application is None:
            raise ValueError("Credit application not found")

        if application.status in self.FINAL_STATUSES:
            raise AssessmentConflictError(
                "Cannot create assessment for a finalized application"
            )

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

    def run_assessment(
        self,
        application_id: UUID,
    ) -> CreditAssessment:
        application = self.application_repository.get_by_id(application_id)

        if application is None:
            raise ValueError("Credit application not found")

        if application.status in self.FINAL_STATUSES:
            raise AssessmentConflictError("Cannot assess a finalized application")

        customer = application.customer

        if (
            customer.monthly_income is None
            or customer.monthly_debt_payments is None
            or customer.employment_months is None
            or customer.employment_status is None
        ):
            raise ValueError("Customer financial profile is incomplete")

        income = Decimal(customer.monthly_income)
        debt_payments = Decimal(customer.monthly_debt_payments)
        requested_amount = Decimal(application.requested_amount)

        if income <= 0:
            raise ValueError("Customer monthly income must be positive")

        estimated_monthly_payment = requested_amount / Decimal(application.term_months)

        total_monthly_debt = debt_payments + estimated_monthly_payment

        dti = total_monthly_debt / income
        loan_to_income = requested_amount / income

        score = 850

        # Debt-to-income ratio.
        if dti > Decimal("0.60"):
            score -= 350
        elif dti > Decimal("0.50"):
            score -= 250
        elif dti > Decimal("0.40"):
            score -= 160
        elif dti > Decimal("0.30"):
            score -= 80

        # Loan amount relative to monthly income.
        if loan_to_income > Decimal("12"):
            score -= 100
        elif loan_to_income > Decimal("6"):
            score -= 60
        elif loan_to_income > Decimal("3"):
            score -= 30

        # Employment stability.
        if customer.employment_months < 6:
            score -= 90
        elif customer.employment_months < 12:
            score -= 60
        elif customer.employment_months < 24:
            score -= 35
        elif customer.employment_months < 60:
            score -= 15

        # Employment status.
        employment_penalties = {
            "employed": 0,
            "self_employed": 20,
            "retired": 25,
            "student": 80,
            "unemployed": 150,
        }

        score -= employment_penalties.get(
            customer.employment_status,
            100,
        )

        score = max(300, min(850, score))

        # Synthetic risk indicator. Not a calibrated PD model.
        if score >= 800:
            probability_of_default = Decimal("0.010000")
        elif score >= 750:
            probability_of_default = Decimal("0.030000")
        elif score >= 650:
            probability_of_default = Decimal("0.070000")
        elif score >= 550:
            probability_of_default = Decimal("0.150000")
        else:
            probability_of_default = Decimal("0.250000")

        features: dict[str, object] = {
            "monthly_income": str(income),
            "monthly_debt_payments": str(debt_payments),
            "requested_amount": str(requested_amount),
            "term_months": application.term_months,
            "estimated_monthly_payment": str(
                estimated_monthly_payment.quantize(Decimal("0.01"))
            ),
            "payment_estimation": "principal_only_no_interest",
            "debt_to_income_ratio": round(float(dti), 4),
            "loan_to_monthly_income_ratio": round(float(loan_to_income), 4),
            "employment_months": customer.employment_months,
            "employment_status": customer.employment_status,
            "model_type": "rule_based",
            "probability_of_default_is_calibrated": False,
        }

        assessment = self.repository.create(
            application_id=application_id,
            probability_of_default=probability_of_default,
            credit_score=score,
            model_name=self.MODEL_NAME,
            model_version=self.MODEL_VERSION,
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
