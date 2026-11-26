from uuid import uuid4

from fastapi.testclient import TestClient


def test_create_decision_returns_201(
    client: TestClient,
    decision_context,
):
    application = decision_context["application"]
    assessment = decision_context["assessment"]

    response = client.post(
        "/api/v1/decisions",
        json={
            "application_id": str(application.id),
            "assessment_id": str(assessment.id),
            "decision_status": "approved",
            "reason": "Credit requirements satisfied",
        },
    )

    assert response.status_code == 201
    assert response.json()["decision_status"] == "approved"
    assert response.json()["application_id"] == str(application.id)


def test_second_final_decision_returns_409(
    client: TestClient,
    decision_context,
):
    application = decision_context["application"]

    payload = {
        "application_id": str(application.id),
        "decision_status": "approved",
    }

    first_response = client.post("/api/v1/decisions", json=payload)
    second_response = client.post(
        "/api/v1/decisions",
        json={**payload, "decision_status": "rejected"},
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_nonexistent_application_returns_400(client: TestClient):
    response = client.post(
        "/api/v1/decisions",
        json={
            "application_id": str(uuid4()),
            "decision_status": "approved",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Credit application not found"


def test_nonexistent_assessment_returns_400(
    client: TestClient,
    decision_context,
):
    application = decision_context["application"]

    response = client.post(
        "/api/v1/decisions",
        json={
            "application_id": str(application.id),
            "assessment_id": str(uuid4()),
            "decision_status": "approved",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Credit assessment not found"


def test_get_decision_returns_200(
    client: TestClient,
    decision_context,
):
    application = decision_context["application"]

    create_response = client.post(
        "/api/v1/decisions",
        json={
            "application_id": str(application.id),
            "decision_status": "manual_review",
        },
    )

    decision_id = create_response.json()["id"]

    response = client.get(f"/api/v1/decisions/{decision_id}")

    assert response.status_code == 200
    assert response.json()["id"] == decision_id


def test_get_nonexistent_decision_returns_404(client: TestClient):
    response = client.get(f"/api/v1/decisions/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Credit decision not found"


def test_get_application_decisions_returns_200(
    client: TestClient,
    decision_context,
):
    application = decision_context["application"]

    for reason in ("First review", "Second review"):
        client.post(
            "/api/v1/decisions",
            json={
                "application_id": str(application.id),
                "decision_status": "manual_review",
                "reason": reason,
            },
        )

    response = client.get(f"/api/v1/decisions/application/{application.id}")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_decisions_for_nonexistent_application_returns_404(
    client: TestClient,
):
    response = client.get(f"/api/v1/decisions/application/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Credit application not found"
