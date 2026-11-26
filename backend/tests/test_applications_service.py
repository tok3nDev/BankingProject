from decimal import Decimal
from uuid import uuid4

import pytest
from app.modules.credit_scoring.models.application import CreditApplication
from app.modules.credit_scoring.models.customer import Customer
from app.modules.credit_scoring.schemas.application import ApplicationCreate
from app.modules.credit_scoring.services.application import ApplicationService
from sqlalchemy.orm import Session


def test_create_application(db_session: Session):
    customer = Customer(full_name="John Smith")
    db_session.add(customer)
    db_session.flush()

    service = ApplicationService(db_session)
    data = ApplicationCreate(
        customer_id=customer.id,
        requested_amount=Decimal("15000.00"),
        currency_code="USD",
        term_months=24,
        purpose="Personal loan",
    )

    application = service.create_application(data)

    assert application.id is not None
    assert application.customer_id == customer.id
    assert application.requested_amount == Decimal("15000.00")
    assert application.status == "pending"


def test_create_application_for_nonexistent_customer_raises_error(
    db_session: Session,
):
    service = ApplicationService(db_session)
    data = ApplicationCreate(
        customer_id=uuid4(),
        requested_amount=Decimal("15000.00"),
        currency_code="USD",
        term_months=24,
        purpose="Personal loan",
    )

    with pytest.raises(ValueError, match="Customer not found"):
        service.create_application(data)


def test_get_existing_application(db_session: Session):
    customer = Customer(full_name="John Smith")
    db_session.add(customer)
    db_session.flush()

    application = CreditApplication(
        customer_id=customer.id,
        requested_amount=Decimal("10000.00"),
        currency_code="USD",
        term_months=12,
        purpose="Personal loan",
    )
    db_session.add(application)
    db_session.flush()

    service = ApplicationService(db_session)
    result = service.get_application(application.id)

    assert result is not None
    assert result.id == application.id


def test_get_nonexistent_application(db_session: Session):
    service = ApplicationService(db_session)

    result = service.get_application(uuid4())

    assert result is None


def test_get_customer_applications(db_session: Session):
    customer = Customer(full_name="John Smith")
    db_session.add(customer)
    db_session.flush()

    db_session.add_all(
        [
            CreditApplication(
                customer_id=customer.id,
                requested_amount=Decimal("10000.00"),
                currency_code="USD",
                term_months=12,
                purpose="Personal loan",
            ),
            CreditApplication(
                customer_id=customer.id,
                requested_amount=Decimal("20000.00"),
                currency_code="USD",
                term_months=24,
                purpose="Home improvement",
            ),
        ]
    )
    db_session.flush()

    service = ApplicationService(db_session)
    applications = service.get_customer_applications(customer.id)

    assert len(applications) == 2
    assert all(item.customer_id == customer.id for item in applications)


def test_get_applications_for_nonexistent_customer_raises_error(
    db_session: Session,
):
    service = ApplicationService(db_session)

    with pytest.raises(ValueError, match="Customer not found"):
        service.get_customer_applications(uuid4())


def test_get_customer_applications_supports_pagination(
    db_session: Session,
):
    customer = Customer(full_name="John Smith")
    db_session.add(customer)
    db_session.flush()

    db_session.add_all(
        [
            CreditApplication(
                customer_id=customer.id,
                requested_amount=Decimal("10000.00"),
                currency_code="USD",
                term_months=12,
                purpose="Personal loan",
            ),
            CreditApplication(
                customer_id=customer.id,
                requested_amount=Decimal("20000.00"),
                currency_code="USD",
                term_months=24,
                purpose="Home improvement",
            ),
        ]
    )
    db_session.flush()

    service = ApplicationService(db_session)
    applications = service.get_customer_applications(
        customer.id,
        offset=1,
        limit=1,
    )

    assert len(applications) == 1


def test_get_all_applications(db_session: Session):
    customer = Customer(full_name="John Smith")
    db_session.add(customer)
    db_session.flush()

    db_session.add_all(
        [
            CreditApplication(
                customer_id=customer.id,
                requested_amount=Decimal("10000.00"),
                currency_code="USD",
                term_months=12,
                purpose="Personal loan",
            ),
            CreditApplication(
                customer_id=customer.id,
                requested_amount=Decimal("20000.00"),
                currency_code="USD",
                term_months=24,
                purpose="Home improvement",
            ),
        ]
    )
    db_session.flush()

    service = ApplicationService(db_session)
    applications = service.get_all_applications()

    assert len(applications) == 2


def test_get_all_applications_supports_pagination(db_session: Session):
    customer = Customer(full_name="John Smith")
    db_session.add(customer)
    db_session.flush()

    db_session.add_all(
        [
            CreditApplication(
                customer_id=customer.id,
                requested_amount=Decimal("10000.00"),
                currency_code="USD",
                term_months=12,
                purpose="Personal loan",
            ),
            CreditApplication(
                customer_id=customer.id,
                requested_amount=Decimal("20000.00"),
                currency_code="USD",
                term_months=24,
                purpose="Home improvement",
            ),
        ]
    )
    db_session.flush()

    service = ApplicationService(db_session)
    applications = service.get_all_applications(offset=1, limit=1)

    assert len(applications) == 1


@pytest.mark.parametrize(
    ("kwargs", "error"),
    [
        ({"offset": -1}, "Offset cannot be negative"),
        ({"limit": 0}, "Limit must be between 1 and 100"),
    ],
)
def test_get_all_applications_validates_pagination(
    db_session: Session,
    kwargs: dict[str, int],
    error: str,
):
    service = ApplicationService(db_session)

    with pytest.raises(ValueError, match=error):
        service.get_all_applications(**kwargs)


@pytest.mark.parametrize(
    ("kwargs", "error"),
    [
        ({"offset": -1}, "Offset cannot be negative"),
        ({"limit": 101}, "Limit must be between 1 and 100"),
    ],
)
def test_get_customer_applications_validates_pagination(
    db_session: Session,
    kwargs: dict[str, int],
    error: str,
):
    customer = Customer(full_name="John Smith")
    db_session.add(customer)
    db_session.flush()

    service = ApplicationService(db_session)

    with pytest.raises(ValueError, match=error):
        service.get_customer_applications(customer.id, **kwargs)
