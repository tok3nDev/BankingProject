from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.credit_scoring.schemas.customer import (
    CustomerCreate,
    CustomerResponse,
)
from app.modules.credit_scoring.services.customer import CustomerService

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer(
    data: CustomerCreate,
    db: Session = Depends(get_db),
) -> CustomerResponse:
    service = CustomerService(db)

    try:
        customer = service.create_customer(data)
        db.commit()
        return CustomerResponse.model_validate(customer)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Customer with this email already exists",
        ) from exc


@router.get(
    "",
    response_model=list[CustomerResponse],
)
def get_customers(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[CustomerResponse]:
    service = CustomerService(db)
    customers = service.get_customers(offset=offset, limit=limit)

    return [CustomerResponse.model_validate(customer) for customer in customers]


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
)
def get_customer(
    customer_id: UUID,
    db: Session = Depends(get_db),
) -> CustomerResponse:
    service = CustomerService(db)
    customer = service.get_customer(customer_id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    return CustomerResponse.model_validate(customer)
