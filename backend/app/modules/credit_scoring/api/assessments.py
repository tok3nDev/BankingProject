from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.credit_scoring.schemas.assessment import (
    AssessmentCreate,
    AssessmentResponse,
)
from app.modules.credit_scoring.services.assessment import (
    AssessmentConflictError,
    AssessmentService,
)

router = APIRouter(prefix="/assessments", tags=["Assessments"])


@router.post(
    "",
    response_model=AssessmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_assessment(
    payload: AssessmentCreate,
    db: Session = Depends(get_db),
) -> AssessmentResponse:
    service = AssessmentService(db)

    try:
        assessment = service.create_assessment(
            application_id=payload.application_id,
            probability_of_default=payload.probability_of_default,
            credit_score=payload.credit_score,
            model_name=payload.model_name,
            model_version=payload.model_version,
            features=payload.features,
        )
        db.commit()
        return AssessmentResponse.model_validate(assessment)

    except AssessmentConflictError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

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


@router.post(
    "/run",
    response_model=AssessmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def run_assessment(
    application_id: UUID,
    db: Session = Depends(get_db),
) -> AssessmentResponse:
    service = AssessmentService(db)

    try:
        assessment = service.run_assessment(application_id)
        db.commit()
        return AssessmentResponse.model_validate(assessment)

    except AssessmentConflictError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Database integrity conflict",
        ) from exc


@router.get(
    "/application/{application_id}",
    response_model=list[AssessmentResponse],
)
def get_application_assessments(
    application_id: UUID,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[AssessmentResponse]:
    service = AssessmentService(db)

    try:
        assessments = service.get_application_assessments(
            application_id,
            offset=offset,
            limit=limit,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return [AssessmentResponse.model_validate(assessment) for assessment in assessments]


@router.get(
    "/{assessment_id}",
    response_model=AssessmentResponse,
)
def get_assessment(
    assessment_id: UUID,
    db: Session = Depends(get_db),
) -> AssessmentResponse:
    service = AssessmentService(db)
    assessment = service.get_assessment(assessment_id)

    if assessment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credit assessment not found",
        )

    return AssessmentResponse.model_validate(assessment)
