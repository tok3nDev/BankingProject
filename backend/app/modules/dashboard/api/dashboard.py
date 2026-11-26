from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.dashboard.schemas.dashboard import DashboardStatsResponse
from app.modules.dashboard.services.dashboard import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/stats",
    response_model=DashboardStatsResponse,
)
def get_dashboard_stats(
    db: Session = Depends(get_db),
) -> DashboardStatsResponse:
    service = DashboardService(db)
    return service.get_stats()
