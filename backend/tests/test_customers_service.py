from decimal import Decimal
from uuid import uuid4

import pytest
from app.modules.credit_scoring.models.customer import Customer
from app.modules.credit_scoring.schemas.customer import CustomerCreate
from app.modules.credit_scoring.services.customer import CustomerService
from sqlalchemy.orm import Session


def test_create_customer(db_session: Session):
    service = CustomerService(db_session)
    data = CustomerCreate(
        full_name="John Smith",
        email="john@example.com",
        monthly_income=Decimal("5000.00"),
        monthly_debt_payments=Decimal("1000.00"),
        employment_months=36,
        employment_status="employed",
    )

    customer = service.create_customer(data)

    assert customer.id is not None
    assert customer.full_name == "John Smith"
    assert customer.email == "john@example.com"
    assert customer.monthly_income == Decimal("5000.00")
    assert customer.monthly_debt_payments == Decimal("1000.00")
    assert customer.employment_months == 36
    assert customer.employment_status == "employed"


def test_create_customer_without_email(db_session: Session):
    service = CustomerService(db_session)
    data = CustomerCreate(
        full_name="Jane Smith",
        monthly_income=Decimal("4000.00"),
        monthly_debt_payments=Decimal("500.00"),
        employment_months=24,
        employment_status="employed",
    )

    customer = service.create_customer(data)

    assert customer.email is None


def test_create_customer_with_duplicate_email_raises_error(
    db_session: Session,
):
    db_session.add(
        Customer(
            full_name="Existing Customer",
            email="existing@example.com",
        )
    )
    db_session.flush()

    service = CustomerService(db_session)
    data = CustomerCreate(
        full_name="Another Customer",
        email="existing@example.com",
        monthly_income=Decimal("5000.00"),
        monthly_debt_payments=Decimal("1000.00"),
        employment_months=36,
        employment_status="employed",
    )

    with pytest.raises(
        ValueError,
        match="Customer with this email already exists",
    ):
        service.create_customer(data)


def test_get_existing_customer(db_session: Session):
    customer = Customer(full_name="John Smith")
    db_session.add(customer)
    db_session.flush()

    service = CustomerService(db_session)
    result = service.get_customer(customer.id)

    assert result is not None
    assert result.id == customer.id


def test_get_nonexistent_customer(db_session: Session):
    service = CustomerService(db_session)

    result = service.get_customer(uuid4())

    assert result is None


def test_get_customers_returns_list(db_session: Session):
    db_session.add_all(
        [
            Customer(full_name="Customer One"),
            Customer(full_name="Customer Two"),
        ]
    )
    db_session.flush()

    service = CustomerService(db_session)
    customers = service.get_customers()

    assert len(customers) == 2


def test_get_customers_supports_pagination(db_session: Session):
    db_session.add_all(
        [
            Customer(full_name="Customer One"),
            Customer(full_name="Customer Two"),
            Customer(full_name="Customer Three"),
        ]
    )
    db_session.flush()

    service = CustomerService(db_session)
    customers = service.get_customers(offset=1, limit=1)

    assert len(customers) == 1


def test_get_customers_with_negative_offset_raises_error(
    db_session: Session,
):
    service = CustomerService(db_session)

    with pytest.raises(ValueError, match="Offset cannot be negative"):
        service.get_customers(offset=-1)


@pytest.mark.parametrize("limit", [0, -1, 101])
def test_get_customers_with_invalid_limit_raises_error(
    db_session: Session,
    limit: int,
):
    service = CustomerService(db_session)

    with pytest.raises(ValueError, match="Limit must be between 1 and 100"):
        service.get_customers(limit=limit)
