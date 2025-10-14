from __future__ import annotations

import asyncio

from datetime import datetime, date, time

from typing import List

from pydantic import BaseModel


from models.sql_dependency_model import SQLBaseDependencyModel
from results.dashboard_config_results import DashboardSQLQueryResult, DashboardSQLQueryParameter
from results.plotly_chart_config_results import BoxChartConfig, ScatterChartConfig, PieChartConfig, LineChartConfig, HistogramChartConfig, BarChartConfig
from results.tool_results import PandasDataFrame, PlotlyFigure

class DashboardSQLQueryParameterValue(BaseModel):
    parameter: DashboardSQLQueryParameter
    value: str | int | float | bool | datetime | date | time
    
class DashboardEvaluationSQLQuery(BaseModel):
    sql_dependency_id: str
    parametrized_query: str
    dashboard_sql_query_parameter_values: List[DashboardSQLQueryParameterValue]
    
    async def evaluate(self, timeout: int = 180) -> PandasDataFrame:
        
        sql_dependency = await SQLBaseDependencyModel.get(pk=self.sql_dependency_id)
        
        evaluated_query = self.parametrized_query
        
        for param_value in self.dashboard_sql_query_parameter_values:
            placeholder = "{" + param_value.parameter.name + "}"
            
            if placeholder not in evaluated_query:
                raise ValueError(f"Parameter '{param_value.parameter.name}' not found in query")
            
            if isinstance(param_value.value, str):
                value_str = f"'{param_value.value}'"
            elif isinstance(param_value.value, bool):
                value_str = 'TRUE' if param_value.value else 'FALSE'
            elif isinstance(param_value.value, (datetime, date, time)):
                value_str = f"'{param_value.value.isoformat()}'"
            else:
                value_str = str(param_value.value)
            
            evaluated_query = evaluated_query.replace(placeholder, value_str)

        df = await asyncio.wait_for(
            fut=asyncio.to_thread(sql_dependency.get_dataframe_from_query, evaluated_query),
            timeout=timeout
        )

        return PandasDataFrame.from_dataframe(df)


class DashboardEvaluationRequest(BaseModel):
    dashboard_evaluation_sql_query: DashboardEvaluationSQLQuery
    figure_configs: List[BoxChartConfig | ScatterChartConfig | PieChartConfig | LineChartConfig | HistogramChartConfig | BarChartConfig]
    
    async def evaluate(self) -> DashboardEvaluationResponse:

        if not self.figure_configs:
            raise ValueError("Figure configuration is not set")
        
        df = await self.dashboard_evaluation_sql_query.evaluate()
        
        figures = [fig.get_figure(dataframe=df.to_dataframe()) for fig in self.figure_configs]
        
        return DashboardEvaluationResponse(
            dashboard_evaluation_request=self,
            data_frame=df,
            figures=figures
        )

class DashboardEvaluationResponse(BaseModel):
    dashboard_evaluation_request: DashboardEvaluationRequest
    data_frame: PandasDataFrame
    figures: List[PlotlyFigure]