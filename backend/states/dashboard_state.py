from __future__ import annotations

from pydantic import BaseModel, computed_field

from aredis_om import NotFoundError

from models.sql_dependency_model import SQLBaseDependencyModel
from states.dashboard_config_state import DashboardConfigState
from results.tool_results import PandasDataFrame, PlotlyFigure
from schemas.dashboard_evaluation import DashboardSQLQueryParameterValue

class DashboardState(BaseModel):
    dashboard_config: DashboardConfigState = DashboardConfigState()
    test_dataframe: PandasDataFrame | None = None
    test_figure: PlotlyFigure | None = None
    selected_sql_dependency_id: str | None = None
    
    async def evaluate_test_dataframe(self) -> PandasDataFrame | None:

        if self.dashboard_config.dashboard_sql_query is None:
            return None
        
        else:
            
            dashboard_parameter_values: list[DashboardSQLQueryParameterValue] = [
                DashboardSQLQueryParameterValue(
                    name=param.name,
                    value=param.default_value
                )
                for param in self.dashboard_config.dashboard_sql_query.dashboard_sql_query_parameters
            ]

            return await self.dashboard_config.dashboard_sql_query.execute_query(dashboard_parameter_values)


    async def get_sql_dependency(self) -> SQLBaseDependencyModel:

        if self.selected_sql_dependency_id is None:
            raise ValueError("No SQL dependency selected")
        
        try:
            return await SQLBaseDependencyModel.get(self.selected_sql_dependency_id)
        
        except NotFoundError:
            raise ValueError(f"SQL dependency with pk {self.selected_sql_dependency_id} not found")