from collections.abc import Generator
from decimal import Decimal
from typing import TypedDict

import pytest
from app.core.config import settings
from app.db.session import get_db
from app.main import app
from app.modules.credit_scoring.models.application import CreditApplication
from app.modules.credit_scoring.models.assessment import CreditAssessment
from app.modules.credit_scoring.models.customer import Customer
from fastapi.testclient import TestClient
from sqlalchemy import Connection, Engine, create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker


@pytest.fixture(scope="session")
def test_engine() -> Generator[Engine, None, None]:
    if not settings.test_database_url:
        raise RuntimeError("TEST_DATABASE_URL is not configured")

    test_url = make_url(settings.test_database_url)
    main_url = make_url(settings.database_url)

    if test_url.database != "banking_test_db":
        raise RuntimeError("Tests can only run against the banking_test_db database")

    if test_url.database == main_url.database:
        raise RuntimeError("Test database must be different from the main database")

    engine = create_engine(
        settings.test_database_url,
        pool_pre_ping=True,
    )

    yield engine

    engine.dispose()


@pytest.fixture
def db_connection(test_engine: Engine) -> Generator[Connection, None, None]:
    connection = test_engine.connect()
    transaction = connection.begin()

    try:
        yield connection
    finally:
        transaction.rollback()
        connection.close()


@pytest.fixture
def db_session(db_connection: Connection) -> Generator[Session, None, None]:
    test_session_factory = sessionmaker(
        bind=db_connection,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    session = test_session_factory()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_connection: Connection) -> Generator[TestClient, None, None]:
    test_session_factory = sessionmaker(
        bind=db_connection,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    def override_get_db() -> Generator[Session, None, None]:
        db = test_session_factory()

        try:
            yield db
        finally:
            db.close()

    previous_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        if previous_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous_override


class DecisionContext(TypedDict):
    customer: Customer
    application: CreditApplication
    assessment: CreditAssessment


@pytest.fixture
def decision_context(db_session: Session) -> DecisionContext:
    customer = Customer(
        full_name="Test Customer",
        email="decision.test@example.com",
    )
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

    assessment = CreditAssessment(
        application_id=application.id,
        probability_of_default=Decimal("0.025"),
        credit_score=750,
        model_name="test-model",
        model_version="1.0",
        features={"income": 5000},
    )
    db_session.add(assessment)
    db_session.flush()

    return {
        "customer": customer,
        "application": application,
        "assessment": assessment,
    }
