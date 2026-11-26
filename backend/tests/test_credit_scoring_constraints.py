from decimal import Decimal

import pytest
from app.modules.credit_scoring.models.application import CreditApplication
from app.modules.credit_scoring.services.decision import (
    DecisionConflictError,
    DecisionService,
)


def test_create_approved_decision_updates_application_status(
    db_session,
    decision_context,
):
    application = decision_context["application"]
    assessment = decision_context["assessment"]

    service = DecisionService(db_session)

    decision = service.create_decision(
        application_id=application.id,
        assessment_id=assessment.id,
        decision_status="approved",
        reason="Credit requirements satisfied",
    )

    assert decision.decision_status == "approved"
    assert decision.application_id == application.id
    assert decision.assessment_id == assessment.id
    assert application.status == "approved"


def test_create_rejected_decision_updates_application_status(
    db_session,
    decision_context,
):
    application = decision_context["application"]

    service = DecisionService(db_session)

    decision = service.create_decision(
        application_id=application.id,
        decision_status="rejected",
        reason="Insufficient creditworthiness",
    )

    assert decision.decision_status == "rejected"
    assert application.status == "rejected"


def test_second_final_decision_is_rejected(
    db_session,
    decision_context,
):
    application = decision_context["application"]

    service = DecisionService(db_session)

    service.create_decision(
        application_id=application.id,
        decision_status="approved",
    )

    with pytest.raises(DecisionConflictError):
        service.create_decision(
            application_id=application.id,
            decision_status="rejected",
        )


def test_multiple_manual_reviews_are_allowed(
    db_session,
    decision_context,
):
    application = decision_context["application"]

    service = DecisionService(db_session)

    first = service.create_decision(
        application_id=application.id,
        decision_status="manual_review",
        reason="First review",
    )

    second = service.create_decision(
        application_id=application.id,
        decision_status="manual_review",
        reason="Second review",
    )

    assert first.id != second.id
    assert application.status == "pending"


def test_assessment_from_another_application_is_rejected(
    db_session,
    decision_context,
):
    customer = decision_context["customer"]

    another_application = CreditApplication(
        customer_id=customer.id,
        requested_amount=Decimal("5000.00"),
        currency_code="USD",
        term_months=6,
        purpose="Another loan",
    )
    db_session.add(another_application)
    db_session.flush()

    assessment = decision_context["assessment"]
    service = DecisionService(db_session)

    with pytest.raises(
        ValueError,
        match="Assessment does not belong to this application",
    ):
        service.create_decision(
            application_id=another_application.id,
            assessment_id=assessment.id,
            decision_status="approved",
        )


def test_decision_for_nonexistent_application_is_rejected(db_session):
    from uuid import uuid4

    service = DecisionService(db_session)

    with pytest.raises(
        ValueError,
        match="Credit application not found",
    ):
        service.create_decision(
            application_id=uuid4(),
            decision_status="approved",
        )
