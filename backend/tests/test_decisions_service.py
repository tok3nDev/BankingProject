from uuid import uuid4

import pytest
from app.modules.credit_scoring.models.application import CreditApplication
from app.modules.credit_scoring.services.decision import (
    DecisionConflictError,
    DecisionService,
)
from sqlalchemy.orm import Session

from tests.conftest import DecisionContext


@pytest.mark.parametrize(
    ("decision_status", "expected_application_status"),
    [
        ("approved", "approved"),
        ("rejected", "rejected"),
    ],
)
def test_create_final_decision_updates_application_status(
    db_session: Session,
    decision_context: DecisionContext,
    decision_status: str,
    expected_application_status: str,
):
    application = decision_context["application"]
    service = DecisionService(db_session)

    decision = service.create_decision(
        application_id=application.id,
        decision_status=decision_status,
        reason="Test decision",
    )

    assert decision.decision_status == decision_status
    assert application.status == expected_application_status


def test_create_manual_review_does_not_update_application_status(
    db_session: Session,
    decision_context: DecisionContext,
):
    application = decision_context["application"]
    service = DecisionService(db_session)

    decision = service.create_decision(
        application_id=application.id,
        decision_status="manual_review",
        reason="Requires additional verification",
    )

    assert decision.decision_status == "manual_review"
    assert application.status == "pending"


def test_create_decision_for_nonexistent_application_raises_error(
    db_session: Session,
):
    service = DecisionService(db_session)

    with pytest.raises(ValueError, match="Credit application not found"):
        service.create_decision(
            application_id=uuid4(),
            decision_status="approved",
        )


def test_create_second_final_decision_raises_conflict(
    db_session: Session,
    decision_context: DecisionContext,
):
    application = decision_context["application"]
    service = DecisionService(db_session)

    service.create_decision(
        application_id=application.id,
        decision_status="approved",
    )

    with pytest.raises(
        DecisionConflictError,
        match="A final decision already exists",
    ):
        service.create_decision(
            application_id=application.id,
            decision_status="rejected",
        )


def test_create_manual_review_after_manual_review_is_allowed(
    db_session: Session,
    decision_context: DecisionContext,
):
    application = decision_context["application"]
    service = DecisionService(db_session)

    first = service.create_decision(
        application_id=application.id,
        decision_status="manual_review",
    )
    second = service.create_decision(
        application_id=application.id,
        decision_status="manual_review",
    )

    assert first.id != second.id
    assert application.status == "pending"


def test_create_decision_with_assessment(
    db_session: Session,
    decision_context: DecisionContext,
):
    application = decision_context["application"]
    assessment = decision_context["assessment"]
    service = DecisionService(db_session)

    decision = service.create_decision(
        application_id=application.id,
        assessment_id=assessment.id,
        decision_status="approved",
    )

    assert decision.assessment_id == assessment.id


def test_create_decision_with_nonexistent_assessment_raises_error(
    db_session: Session,
    decision_context: DecisionContext,
):
    application = decision_context["application"]
    service = DecisionService(db_session)

    with pytest.raises(ValueError, match="Credit assessment not found"):
        service.create_decision(
            application_id=application.id,
            assessment_id=uuid4(),
            decision_status="approved",
        )


def test_create_decision_with_assessment_from_another_application_raises_error(
    db_session: Session,
    decision_context: DecisionContext,
):
    application = decision_context["application"]
    assessment = decision_context["assessment"]
    other_application = CreditApplication(
        customer_id=decision_context["customer"].id,
        requested_amount=application.requested_amount,
        currency_code=application.currency_code,
        term_months=application.term_months,
        purpose=application.purpose,
    )
    db_session.add(other_application)
    db_session.flush()

    service = DecisionService(db_session)

    with pytest.raises(
        ValueError,
        match="Assessment does not belong to this application",
    ):
        service.create_decision(
            application_id=other_application.id,
            assessment_id=assessment.id,
            decision_status="approved",
        )


def test_get_existing_decision(
    db_session: Session,
    decision_context: DecisionContext,
):
    application = decision_context["application"]
    service = DecisionService(db_session)

    created = service.create_decision(
        application_id=application.id,
        decision_status="manual_review",
    )
    result = service.get_decision(created.id)

    assert result is not None
    assert result.id == created.id


def test_get_nonexistent_decision(db_session: Session):
    service = DecisionService(db_session)

    result = service.get_decision(uuid4())

    assert result is None


def test_get_application_decisions(
    db_session: Session,
    decision_context: DecisionContext,
):
    application = decision_context["application"]
    service = DecisionService(db_session)

    service.create_decision(
        application_id=application.id,
        decision_status="manual_review",
    )
    service.create_decision(
        application_id=application.id,
        decision_status="manual_review",
    )

    decisions = service.get_application_decisions(application.id)

    assert len(decisions) == 2


def test_get_application_decisions_supports_pagination(
    db_session: Session,
    decision_context: DecisionContext,
):
    application = decision_context["application"]
    service = DecisionService(db_session)

    service.create_decision(
        application_id=application.id,
        decision_status="manual_review",
    )
    service.create_decision(
        application_id=application.id,
        decision_status="manual_review",
    )

    decisions = service.get_application_decisions(
        application.id,
        offset=1,
        limit=1,
    )

    assert len(decisions) == 1


def test_get_decisions_for_nonexistent_application_raises_error(
    db_session: Session,
):
    service = DecisionService(db_session)

    with pytest.raises(ValueError, match="Credit application not found"):
        service.get_application_decisions(uuid4())


@pytest.mark.parametrize(
    ("kwargs", "error"),
    [
        ({"offset": -1}, "Offset cannot be negative"),
        ({"limit": 0}, "Limit must be between 1 and 100"),
        ({"limit": 101}, "Limit must be between 1 and 100"),
    ],
)
def test_get_application_decisions_validates_pagination(
    db_session: Session,
    decision_context: DecisionContext,
    kwargs: dict[str, int],
    error: str,
):
    service = DecisionService(db_session)
    application = decision_context["application"]

    with pytest.raises(ValueError, match=error):
        service.get_application_decisions(application.id, **kwargs)
