from pydantic import BaseModel

from deps.sql_dependency import SQLBaseDependency
from results.dashboard_config_results import DashboardConfig


class DashboardState(BaseModel):
    sql_dependency: SQLBaseDependency
    state: DashboardConfig | None = None