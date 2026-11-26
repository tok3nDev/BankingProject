from uuid import uuid4

from app.modules.credit_scoring.models.customer import Customer
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_create_customer_returns_201(client: TestClient):
    response = client.post(
        "/api/v1/customers",
        json={
            "full_name": "John Smith",
            "date_of_birth": "1990-05-15",
            "email": "john.smith@example.com",
        },
    )

    assert response.status_code == 201
    assert response.json()["full_name"] == "John Smith"
    assert response.json()["email"] == "john.smith@example.com"
    assert response.json()["date_of_birth"] == "1990-05-15"
    assert "id" in response.json()


def test_create_customer_without_email_returns_201(client: TestClient):
    response = client.post(
        "/api/v1/customers",
        json={"full_name": "Jane Smith"},
    )

    assert response.status_code == 201
    assert response.json()["full_name"] == "Jane Smith"
    assert response.json()["email"] is None


def test_create_customer_with_duplicate_email_returns_409(
    client: TestClient,
    db_session: Session,
):
    db_session.add(
        Customer(
            full_name="Existing Customer",
            email="existing@example.com",
        )
    )
    db_session.flush()

    response = client.post(
        "/api/v1/customers",
        json={
            "full_name": "Another Customer",
            "email": "existing@example.com",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == ("Customer with this email already exists")


def test_create_customer_with_invalid_data_returns_422(
    client: TestClient,
):
    response = client.post(
        "/api/v1/customers",
        json={
            "full_name": "A",
            "email": "invalid-email",
        },
    )

    assert response.status_code == 422


def test_get_customers_returns_200(
    client: TestClient,
    db_session: Session,
):
    db_session.add(Customer(full_name="Test Customer"))
    db_session.flush()

    response = client.get("/api/v1/customers")

    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_customers_supports_pagination(
    client: TestClient,
    db_session: Session,
):
    db_session.add_all(
        [
            Customer(full_name="Customer One"),
            Customer(full_name="Customer Two"),
            Customer(full_name="Customer Three"),
        ]
    )
    db_session.flush()

    response = client.get(
        "/api/v1/customers",
        params={"offset": 0, "limit": 2},
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_customers_with_invalid_pagination_returns_422(
    client: TestClient,
):
    response = client.get(
        "/api/v1/customers",
        params={"offset": -1},
    )

    assert response.status_code == 422


def test_get_customer_returns_200(
    client: TestClient,
    db_session: Session,
):
    customer = Customer(
        full_name="John Smith",
        email="john@example.com",
    )
    db_session.add(customer)
    db_session.flush()

    response = client.get(f"/api/v1/customers/{customer.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(customer.id)
    assert response.json()["full_name"] == "John Smith"


def test_get_nonexistent_customer_returns_404(
    client: TestClient,
):
    response = client.get(f"/api/v1/customers/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"
