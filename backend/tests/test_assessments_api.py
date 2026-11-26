from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.conftest import DecisionContext


def test_create_assessment_returns_201(
    client: TestClient,
    decision_context: DecisionContext,
):
    application = decision_context["application"]

    response = client.post(
        "/api/v1/assessments",
        json={
            "application_id": str(application.id),
            "probability_of_default": "0.025",
            "credit_score": 750,
            "model_name": "test-model",
            "model_version": "1.0",
            "features": {"income": 5000},
        },
    )

    assert response.status_code == 201
    assert response.json()["application_id"] == str(application.id)
    assert response.json()["credit_score"] == 750
    assert response.json()["model_name"] == "test-model"


def test_create_assessment_for_nonexistent_application_returns_404(
    client: TestClient,
):
    response = client.post(
        "/api/v1/assessments",
        json={
            "application_id": str(uuid4()),
            "probability_of_default": "0.025",
            "credit_score": 750,
            "model_name": "test-model",
            "model_version": "1.0",
            "features": {},
        },
    )

    assert response.status_code == 404


def test_create_assessment_for_finalized_application_returns_409(
    client: TestClient,
    decision_context: DecisionContext,
    db_session: Session,
):
    application = decision_context["application"]

    application.status = "approved"
    db_session.flush()

    response = client.post(
        "/api/v1/assessments",
        json={
            "application_id": str(application.id),
            "probability_of_default": "0.025",
            "credit_score": 750,
            "model_name": "test-model",
            "model_version": "1.0",
            "features": {},
        },
    )

    assert response.status_code == 409


def test_create_assessment_with_invalid_payload_returns_422(
    client: TestClient,
    decision_context: DecisionContext,
):
    application = decision_context["application"]

    response = client.post(
        "/api/v1/assessments",
        json={
            "application_id": str(application.id),
            "probability_of_default": "1.5",
            "credit_score": 750,
            "model_name": "test-model",
            "model_version": "1.0",
            "features": {},
        },
    )

    assert response.status_code == 422


def test_get_assessment_returns_200(
    client: TestClient,
    decision_context: DecisionContext,
):
    assessment = decision_context["assessment"]

    response = client.get(f"/api/v1/assessments/{assessment.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(assessment.id)


def test_get_nonexistent_assessment_returns_404(
    client: TestClient,
):
    response = client.get(f"/api/v1/assessments/{uuid4()}")

    assert response.status_code == 404


def test_get_application_assessments_returns_200(
    client: TestClient,
    decision_context: DecisionContext,
):
    application = decision_context["application"]

    response = client.get(f"/api/v1/assessments/application/{application.id}")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["application_id"] == str(application.id)


def test_get_assessments_for_nonexistent_application_returns_404(
    client: TestClient,
):
    response = client.get(f"/api/v1/assessments/application/{uuid4()}")

    assert response.status_code == 404


def test_get_application_assessments_with_invalid_pagination_returns_422(
    client: TestClient,
    decision_context: DecisionContext,
):
    application = decision_context["application"]

    response = client.get(f"/api/v1/assessments/application/{application.id}?limit=101")

    assert response.status_code == 422
