from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict

ApplicationStatus = Literal[
    "pending",
    "assessed",
    "approved",
    "rejected",
    "withdrawn",
]


class RequestedAmountByCurrency(BaseModel):
    currency_code: str
    total_amount: Decimal


class RecentApplication(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    customer_name: str
    requested_amount: Decimal
    currency_code: str
    purpose: str
    status: ApplicationStatus
    created_at: datetime


class DashboardStatsResponse(BaseModel):
    total_customers: int
    total_applications: int
    pending_applications: int
    assessed_applications: int
    approved_applications: int
    rejected_applications: int
    withdrawn_applications: int
    requested_amount_by_currency: list[RequestedAmountByCurrency]
    recent_applications: list[RecentApplication]
