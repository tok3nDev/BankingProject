from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

EmploymentStatus = Literal[
    "employed",
    "self_employed",
    "unemployed",
    "student",
    "retired",
]


class CustomerCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    date_of_birth: date | None = None
    email: EmailStr | None = None
    monthly_income: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    monthly_debt_payments: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    employment_months: int = Field(ge=0, le=1200)
    employment_status: EmploymentStatus


class CustomerUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=150)
    date_of_birth: date | None = None
    email: EmailStr | None = None
    monthly_income: Decimal | None = Field(
        default=None, gt=0, max_digits=12, decimal_places=2
    )
    monthly_debt_payments: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=2
    )
    employment_months: int | None = Field(default=None, ge=0, le=1200)
    employment_status: EmploymentStatus | None = None


class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    date_of_birth: date | None
    email: EmailStr | None
    monthly_income: Decimal | None
    monthly_debt_payments: Decimal | None
    employment_months: int | None
    employment_status: str | None
    created_at: datetime
