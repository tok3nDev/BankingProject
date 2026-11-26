from typing import TypedDict
from uuid import uuid4

from app.modules.credit_scoring.models.application import CreditApplication
from app.modules.credit_scoring.models.assessment import CreditAssessment
from app.modules.credit_scoring.models.customer import Customer
from fastapi.testclient import TestClient


class DecisionContext(TypedDict):
    customer: Customer
    application: CreditApplication
    assessment: CreditAssessment


def test_create_application_returns_201(
    client: TestClient,
    decision_context: DecisionContext,
):
    customer = decision_context["customer"]

    response = client.post(
        "/api/v1/applications",
        json={
            "customer_id": str(customer.id),
            "requested_amount": "15000.00",
            "currency_code": "USD",
            "term_months": 24,
            "purpose": "Personal loan",
        },
    )

    assert response.status_code == 201
    assert response.json()["customer_id"] == str(customer.id)
    assert response.json()["status"] == "pending"


def test_create_application_for_nonexistent_customer_returns_404(
    client: TestClient,
):
    response = client.post(
        "/api/v1/applications",
        json={
            "customer_id": str(uuid4()),
            "requested_amount": "15000.00",
            "currency_code": "USD",
            "term_months": 24,
            "purpose": "Personal loan",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"


def test_create_application_with_invalid_data_returns_422(
    client: TestClient,
    decision_context: DecisionContext,
):
    customer = decision_context["customer"]

    response = client.post(
        "/api/v1/applications",
        json={
            "customer_id": str(customer.id),
            "requested_amount": "-100.00",
            "currency_code": "INVALID",
            "term_months": 500,
            "purpose": "A",
        },
    )

    assert response.status_code == 422


def test_get_all_applications_returns_200(
    client: TestClient,
    decision_context: DecisionContext,
):
    response = client.get("/api/v1/applications")

    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_application_returns_200(
    client: TestClient,
    decision_context: DecisionContext,
):
    application = decision_context["application"]

    response = client.get(f"/api/v1/applications/{application.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(application.id)


def test_get_nonexistent_application_returns_404(
    client: TestClient,
):
    response = client.get(f"/api/v1/applications/{uuid4()}")

    assert response.status_code == 404


def test_get_customer_applications_returns_200(
    client: TestClient,
    decision_context: DecisionContext,
):
    customer = decision_context["customer"]

    response = client.get(f"/api/v1/applications/customer/{customer.id}")

    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_applications_for_nonexistent_customer_returns_404(
    client: TestClient,
):
    response = client.get(f"/api/v1/applications/customer/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"


def test_get_applications_with_invalid_pagination_returns_422(
    client: TestClient,
):
    response = client.get(
        "/api/v1/applications",
        params={"offset": -1, "limit": 0},
    )

    assert response.status_code == 422
