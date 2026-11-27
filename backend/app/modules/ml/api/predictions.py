from fastapi import APIRouter, HTTPException, status
from pydantic import ValidationError

from app.modules.ml.schemas.prediction import (
    MLHealthResponse,
    ModelInfoResponse,
    PredictionRequest,
    PredictionResponse,
)
from app.modules.ml.services.prediction import (
    ModelUnavailableError,
    check_model_availability,
    make_prediction,
    read_model_metadata,
)

router = APIRouter(prefix="/ml", tags=["machine-learning"])


@router.get("/health", response_model=MLHealthResponse)
def ml_health() -> dict:
    return check_model_availability()


@router.get("/model-info", response_model=ModelInfoResponse)
def get_model_info() -> ModelInfoResponse:
    try:
        metadata = read_model_metadata()
        return ModelInfoResponse.model_validate(metadata)
    except ModelUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model metadata has an invalid structure",
        ) from exc


@router.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest) -> dict:
    try:
        return make_prediction(payload.model_dump(by_alias=True))
    except ModelUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
