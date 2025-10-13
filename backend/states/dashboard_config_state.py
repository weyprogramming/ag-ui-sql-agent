from datetime import date, datetime, time
from typing import List

from pydantic import BaseModel


from results.plotly_chart_config_results import BoxChartConfig, ScatterChartConfig, PieChartConfig, LineChartConfig, HistogramChartConfig, BarChartConfig
from results.tool_results import PandasDataFrame, PlotlyFigure
from results.dashboard_config_results import DashboardSQLQueryResult
from schemas.dashboard_evaluation import DashboardSQLQueryParameterValue, DashboardSQLQueryParameter, DashboardEvaluationRequest, DashboardEvaluationResponse, DashboardEvaluationSQLQuery
from models.sql_dependency_model import SQLBaseDependencyModel



class DashboardSQLQueryState(DashboardSQLQueryResult):
    sql_dependency_id: str
    
    async def get_sql_dependency(self) -> SQLBaseDependencyModel:
        return await SQLBaseDependencyModel.get(self.sql_dependency_id)


class DashboardConfigState(BaseModel):
    dashboard_sql_query: DashboardSQLQueryState | None = None
    chart_config: BoxChartConfig | ScatterChartConfig | PieChartConfig | LineChartConfig | HistogramChartConfig | BarChartConfig | None = None
    
    async def get_default_values_result(self) -> DashboardEvaluationResponse:
        
        if self.dashboard_sql_query is None or self.chart_config is None:
            raise ValueError("Dashboard SQL query or chart configuration is not set")
        
        parameter_values: List[DashboardSQLQueryParameterValue] = [
            DashboardSQLQueryParameterValue(
                parameter=param,
                value=param.default_value
            )
            for param in self.dashboard_sql_query.dashboard_sql_query_parameters
        ]
        
        evaluation_request = DashboardEvaluationRequest(
            dashboard_evaluation_sql_query=DashboardEvaluationSQLQuery(
                sql_dependency_id=self.dashboard_sql_query.sql_dependency_id,
                parametrized_query=self.dashboard_sql_query.parametrized_query,
                dashboard_sql_query_parameter_values=parameter_values
            ),
            chart_config=self.chart_config
        )
        
        return await evaluation_request.evaluate()
        
        