from dataclasses import dataclass

from pydantic import BaseModel

from deps.sql_dependency import SQLBaseDependency
from results.dashboard_config_results import DashboardConfig
from results.tool_results import PandasDataFrame, PlotlyFigure

class DashboardState(BaseModel):
    dashboard_config: DashboardConfig | None = None
    test_dateframe: PandasDataFrame | None = None
    test_figure: PlotlyFigure | None = None
    selected_sql_dependency: str | None = None

@dataclass
class State:
    sql_dependency: SQLBaseDependency
    state: DashboardState