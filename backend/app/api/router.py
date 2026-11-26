from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.modules.credit_scoring.api.applications import router as applications_router
from app.modules.credit_scoring.api.assessments import router as assessments_router
from app.modules.credit_scoring.api.customers import router as customers_router
from app.modules.credit_scoring.api.decisions import router as decisions_router
from app.modules.dashboard.api.dashboard import router as dashboard_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["health"])
api_router.include_router(customers_router)
api_router.include_router(applications_router)
api_router.include_router(assessments_router)
api_router.include_router(decisions_router)
api_router.include_router(dashboard_router)
