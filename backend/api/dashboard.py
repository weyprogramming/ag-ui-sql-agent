from typing import List

from fastapi import APIRouter

from models.dashboard_config_models import DashboardConfig, DashboardConfigModel

router = APIRouter()

@router.post("/dashboard-config")
async def create_dashboard_config(
    dashboard_config: DashboardConfig
) -> DashboardConfig:
    dashboard_config_model = DashboardConfigModel.model_validate(dashboard_config)
    await dashboard_config_model.save()
    return dashboard_config_model
    
@router.get("/dashboard-config")
async def get_dashboards() -> List[DashboardConfigModel]:
    pks = await DashboardConfigModel.all_pks()
    dashboard_configs = []
    
    async for pk in pks:
        dashboard_config = await DashboardConfigModel.get(pk)
        dashboard_configs.append(dashboard_config)
        
    return dashboard_configs

