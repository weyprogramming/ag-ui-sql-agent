from fastapi import APIRouter

from deps.current_sql_dep import current_sql_dep
from results.dashboard_config_results import DashboardConfig
from schemas.dashboard_evaluation import DashboardEvaluationResult, DashboardEvaluationRequest

dashboard_evaluation_router = APIRouter()


@dashboard_evaluation_router.post("/dashboard-evaluation")
async def evaluate_dashboard(
    dashboard_evaluation_request: DashboardEvaluationRequest
) -> DashboardEvaluationResult:
    return current_sql_dep.execute_dashboard_evaluation(dashboard_evaluation_request=dashboard_evaluation_request)