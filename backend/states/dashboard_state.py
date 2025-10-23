from __future__ import annotations
from typing import List

from pydantic import BaseModel, computed_field

from aredis_om import NotFoundError

from models.sql_dependency_model import SQLBaseDependencyModel
from states.dashboard_config_state import DashboardConfigState
from results.tool_results import PandasDataFrame, PlotlyFigure
from schemas.dashboard_evaluation import DashboardSQLQueryParameterValue, DashboardEvaluationSQLQuery

class DashboardState(BaseModel):
    dashboard_config: DashboardConfigState = DashboardConfigState()
    default_dataframe: PandasDataFrame | None = None
    default_figures: List[PlotlyFigure] = []
    selected_sql_dependency_id: str | None = None

    async def evaluate_default_dataframe(self) -> None:
        if self.dashboard_config is None:
            raise ValueError("Dashboard configuration is not set")
        
        if self.dashboard_config.dashboard_sql_query is None:
            raise ValueError("Dashboard SQL query is not set")
        
        dashboard_evaluation_sql_query = DashboardEvaluationSQLQuery(
            sql_dependency_id=self.dashboard_config.dashboard_sql_query.sql_dependency_id,
            parametrized_query=self.dashboard_config.dashboard_sql_query.parametrized_query,
            dashboard_sql_query_parameter_values=[
                DashboardSQLQueryParameterValue(
                    parameter=param,
                    value=param.default_value
                )
                for param in self.dashboard_config.dashboard_sql_query.dashboard_sql_query_parameters
            ]
        )
        
        default_dataframe = await dashboard_evaluation_sql_query.evaluate()
        self.default_dataframe = default_dataframe
        
        
    def evaluate_default_figures(self) -> None:
        if self.default_dataframe is None:
            raise ValueError("Default dataframe is not set")

        if not self.dashboard_config.figure_configs:
            raise ValueError("Figure configuration is not set")

        self.default_figures = [fig.get_figure(dataframe=self.default_dataframe.to_dataframe()) for fig in self.dashboard_config.figure_configs]

    async def get_sql_dependency(self) -> SQLBaseDependencyModel:

        if self.selected_sql_dependency_id is None:
            raise ValueError("No SQL dependency selected")
        
        try:
            return await SQLBaseDependencyModel.get(self.selected_sql_dependency_id)
        
        except NotFoundError:
            raise ValueError(f"SQL dependency with pk {self.selected_sql_dependency_id} not found")