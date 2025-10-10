from fastapi import APIRouter

from schemas.dashboard_evaluation import DashboardEvaluationResult, DashboardEvaluationRequest

dashboard_evaluation_router = APIRouter()


@dashboard_evaluation_router.post("/dashboard-evaluation")
async def evaluate_dashboard(
    dashboard_evaluation_request: DashboardEvaluationRequest
) -> DashboardEvaluationResult:
    pass