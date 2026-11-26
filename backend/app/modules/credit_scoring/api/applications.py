from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.credit_scoring.schemas.application import (
    ApplicationCreate,
    ApplicationResponse,
)
from app.modules.credit_scoring.services.application import ApplicationService

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.get(
    "",
    response_model=list[ApplicationResponse],
)
def get_all_applications(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[ApplicationResponse]:
    service = ApplicationService(db)

    applications = service.get_all_applications(
        offset=offset,
        limit=limit,
    )

    return [
        ApplicationResponse.model_validate(application) for application in applications
    ]


@router.post(
    "",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_application(
    data: ApplicationCreate,
    db: Session = Depends(get_db),
) -> ApplicationResponse:
    service = ApplicationService(db)

    try:
        application = service.create_application(data)
        db.commit()
        return ApplicationResponse.model_validate(application)

    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Database integrity conflict",
        ) from exc


@router.get(
    "/customer/{customer_id}",
    response_model=list[ApplicationResponse],
)
def get_customer_applications(
    customer_id: UUID,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[ApplicationResponse]:
    service = ApplicationService(db)

    try:
        applications = service.get_customer_applications(
            customer_id,
            offset=offset,
            limit=limit,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return [
        ApplicationResponse.model_validate(application) for application in applications
    ]


@router.get(
    "/{application_id}",
    response_model=ApplicationResponse,
)
def get_application(
    application_id: UUID,
    db: Session = Depends(get_db),
) -> ApplicationResponse:
    service = ApplicationService(db)
    application = service.get_application(application_id)

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credit application not found",
        )

    return ApplicationResponse.model_validate(application)
