from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DecisionCreate(BaseModel):
    application_id: UUID
    assessment_id: UUID | None = None
    decision_status: str = Field(pattern=r"^(approved|rejected|manual_review)$")
    reason: str | None = None


class DecisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    application_id: UUID
    assessment_id: UUID | None
    decision_status: str
    reason: str | None
    decided_at: datetime
