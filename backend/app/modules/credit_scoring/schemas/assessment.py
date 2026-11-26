from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AssessmentCreate(BaseModel):
    application_id: UUID
    probability_of_default: Decimal = Field(
        ge=0,
        le=1,
        max_digits=7,
        decimal_places=6,
    )
    credit_score: int = Field(ge=0, le=1000)
    model_name: str = Field(min_length=1, max_length=100)
    model_version: str = Field(min_length=1, max_length=50)
    features: dict[str, object]


class AssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    application_id: UUID
    probability_of_default: Decimal
    credit_score: int
    model_name: str
    model_version: str
    features: dict[str, object]
    evaluated_at: datetime
