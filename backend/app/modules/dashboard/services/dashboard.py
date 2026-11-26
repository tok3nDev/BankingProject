from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.credit_scoring.models.application import CreditApplication
from app.modules.credit_scoring.models.customer import Customer
from app.modules.dashboard.schemas.dashboard import (
    DashboardStatsResponse,
    RecentApplication,
    RequestedAmountByCurrency,
)


class DashboardService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_stats(self) -> DashboardStatsResponse:
        total_customers = self.db.scalar(select(func.count(Customer.id))) or 0

        total_applications = (
            self.db.scalar(select(func.count(CreditApplication.id))) or 0
        )

        status_counts = self.db.execute(
            select(
                CreditApplication.status,
                func.count(CreditApplication.id),
            ).group_by(CreditApplication.status)
        ).all()

        counts = {
            "pending": 0,
            "assessed": 0,
            "approved": 0,
            "rejected": 0,
            "withdrawn": 0,
        }

        for application_status, count in status_counts:
            counts[application_status] = count

        amount_rows = self.db.execute(
            select(
                CreditApplication.currency_code,
                func.sum(CreditApplication.requested_amount),
            )
            .group_by(CreditApplication.currency_code)
            .order_by(CreditApplication.currency_code)
        ).all()

        requested_amount_by_currency = [
            RequestedAmountByCurrency(
                currency_code=currency_code,
                total_amount=total_amount if total_amount is not None else Decimal("0"),
            )
            for currency_code, total_amount in amount_rows
        ]

        recent_rows = self.db.execute(
            select(
                CreditApplication.id,
                Customer.full_name,
                CreditApplication.requested_amount,
                CreditApplication.currency_code,
                CreditApplication.purpose,
                CreditApplication.status,
                CreditApplication.created_at,
            )
            .join(
                Customer,
                Customer.id == CreditApplication.customer_id,
            )
            .order_by(CreditApplication.created_at.desc())
            .limit(5)
        ).all()

        recent_applications = [
            RecentApplication(
                id=str(row.id),
                customer_name=row.full_name,
                requested_amount=row.requested_amount,
                currency_code=row.currency_code,
                purpose=row.purpose,
                status=row.status,
                created_at=row.created_at,
            )
            for row in recent_rows
        ]

        return DashboardStatsResponse(
            total_customers=total_customers,
            total_applications=total_applications,
            pending_applications=counts["pending"],
            assessed_applications=counts["assessed"],
            approved_applications=counts["approved"],
            rejected_applications=counts["rejected"],
            withdrawn_applications=counts["withdrawn"],
            requested_amount_by_currency=requested_amount_by_currency,
            recent_applications=recent_applications,
        )
