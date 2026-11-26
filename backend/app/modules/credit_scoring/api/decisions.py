from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.credit_scoring.schemas.decision import (
    DecisionCreate,
    DecisionResponse,
)
from app.modules.credit_scoring.services.decision import DecisionService

router = APIRouter(prefix="/decisions", tags=["Decisions"])


@router.post(
    "",
    response_model=DecisionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_decision(
    data: DecisionCreate,
    db: Session = Depends(get_db),
) -> DecisionResponse:
    service = DecisionService(db)

    try:
        decision = service.create_decision(
            application_id=data.application_id,
            assessment_id=data.assessment_id,
            decision_status=data.decision_status,
            reason=data.reason,
        )
        db.commit()
        return DecisionResponse.model_validate(decision)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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
    response_model=list[DecisionResponse],
)
def get_application_decisions(
    application_id: UUID,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[DecisionResponse]:
    service = DecisionService(db)

    decisions = service.get_application_decisions(
        application_id,
        offset=offset,
        limit=limit,
    )

    return [DecisionResponse.model_validate(decision) for decision in decisions]


@router.get(
    "/{decision_id}",
    response_model=DecisionResponse,
)
def get_decision(
    decision_id: UUID,
    db: Session = Depends(get_db),
) -> DecisionResponse:
    service = DecisionService(db)
    decision = service.get_decision(decision_id)

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credit decision not found",
        )

    return DecisionResponse.model_validate(decision)
