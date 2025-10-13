from typing import List

from fastapi import APIRouter

from models.dashboard_config_models import DashboardConfigModel
from states.dashboard_config_state import DashboardConfigState
from schemas.dashboard_evaluation import DashboardEvaluationRequest, DashboardEvaluationResponse

dashboard_config_router = APIRouter()
    
@dashboard_config_router.get("/dashboard-config")
async def get_dashboards() -> List[DashboardConfigModel]:
    pks = await DashboardConfigModel.all_pks()
    dashboard_configs = []
    
    async for pk in pks:
        dashboard_config = await DashboardConfigModel.get(pk)
        dashboard_configs.append(dashboard_config)
        
    return dashboard_configs

@dashboard_config_router.post("/dashboard-config")
async def create_dashboard_config(
    dashboard_config: DashboardConfigState
) -> DashboardConfigModel:
    dashboard_config_model = DashboardConfigModel.model_validate(
        obj=dashboard_config
    )
    await dashboard_config_model.save()
    return dashboard_config_model

@dashboard_config_router.post("/dashboard-config/evaluate-state")
async def evaluate_dashboard_config_from_state(
    dashboard_evaluation_request: DashboardEvaluationRequest
) -> DashboardEvaluationResponse:
    return await dashboard_evaluation_request.evaluate()