from typing import List

from fastapi import APIRouter

from models.dashboard_config_models import DashboardConfigModel

router = APIRouter()
    
@router.get("/dashboard-config")
async def get_dashboards() -> List[DashboardConfigModel]:
    pks = await DashboardConfigModel.all_pks()
    dashboard_configs = []
    
    async for pk in pks:
        dashboard_config = await DashboardConfigModel.get(pk)
        dashboard_configs.append(dashboard_config)
        
    return dashboard_configs