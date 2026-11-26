from decimal import Decimal
from uuid import uuid4

import pytest
from app.modules.credit_scoring.services.assessment import (
    AssessmentConflictError,
    AssessmentService,
)
from sqlalchemy.orm import Session


@pytest.mark.parametrize("final_status", ["approved", "rejected", "withdrawn"])
def test_assessment_for_finalized_application_is_rejected(
    db_session: Session,
    decision_context: dict,
    final_status: str,
):
    application = decision_context["application"]
    application.status = final_status
    db_session.flush()

    service = AssessmentService(db_session)

    with pytest.raises(AssessmentConflictError):
        service.create_assessment(
            application_id=application.id,
            probability_of_default=Decimal("0.05"),
            credit_score=700,
            model_name="test-model",
            model_version="1.0",
            features={"income": 5000},
        )

    assert application.status == final_status


def test_create_assessment_updates_application_status(
    db_session: Session,
    decision_context: dict,
):
    application = decision_context["application"]
    application.status = "pending"
    db_session.flush()

    service = AssessmentService(db_session)

    assessment = service.create_assessment(
        application_id=application.id,
        probability_of_default=Decimal("0.05"),
        credit_score=700,
        model_name="test-model",
        model_version="1.0",
        features={"income": 5000},
    )

    assert assessment.application_id == application.id
    assert application.status == "assessed"


def test_create_assessment_for_assessed_application_is_allowed(
    db_session: Session,
    decision_context: dict,
):
    application = decision_context["application"]
    application.status = "assessed"
    db_session.flush()

    service = AssessmentService(db_session)

    assessment = service.create_assessment(
        application_id=application.id,
        probability_of_default=Decimal("0.03"),
        credit_score=750,
        model_name="test-model",
        model_version="1.0",
        features={"income": 6000},
    )

    assert assessment.application_id == application.id
    assert application.status == "assessed"


def test_create_assessment_for_nonexistent_application_is_rejected(
    db_session: Session,
):
    service = AssessmentService(db_session)

    with pytest.raises(
        ValueError,
        match="Credit application not found",
    ):
        service.create_assessment(
            application_id=uuid4(),
            probability_of_default=Decimal("0.05"),
            credit_score=700,
            model_name="test-model",
            model_version="1.0",
            features={},
        )


def test_get_assessments_for_nonexistent_application_is_rejected(
    db_session: Session,
):
    service = AssessmentService(db_session)

    with pytest.raises(
        ValueError,
        match="Credit application not found",
    ):
        service.get_application_assessments(uuid4())


def test_create_assessment_preserves_application_data(
    db_session: Session,
    decision_context: dict,
):
    application = decision_context["application"]
    original_amount = application.requested_amount
    original_customer_id = application.customer_id

    service = AssessmentService(db_session)

    service.create_assessment(
        application_id=application.id,
        probability_of_default=Decimal("0.02"),
        credit_score=800,
        model_name="test-model",
        model_version="1.0",
        features={"income": 7000},
    )

    assert application.requested_amount == original_amount
    assert application.customer_id == original_customer_id
    assert application.status == "assessed"
