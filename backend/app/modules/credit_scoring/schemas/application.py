from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ApplicationCreate(BaseModel):
    customer_id: UUID
    requested_amount: Decimal = Field(
        gt=0,
        max_digits=14,
        decimal_places=2,
    )
    currency_code: str = Field(pattern=r"^[A-Z]{3}$")
    term_months: int = Field(gt=0, le=360)
    purpose: str = Field(min_length=2, max_length=100)


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    customer_id: UUID
    requested_amount: Decimal
    currency_code: str
    term_months: int
    purpose: str
    status: str
    created_at: datetime
    updated_at: datetime
