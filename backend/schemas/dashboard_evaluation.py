from __future__ import annotations

from datetime import datetime, date, time

from typing import List

from pydantic import BaseModel


from results.dashboard_config_results import DashboardConfig, DashboardSQLQueryParameter
from results.plotly_chart_config_results import BoxChartConfig, ScatterChartConfig, PieChartConfig, LineChartConfig, HistogramChartConfig, BarChartConfig
from results.tool_results import PandasDataFrame, PlotlyFigure

class DashboardSQLQueryParameterValue(BaseModel):
    parameter_config: DashboardSQLQueryParameter
    value: str | int | float | bool | datetime | date | time
    
class DashboardEvaluationSQLQuery(BaseModel):
    parametrized_query: str
    dashboard_sql_query_parameter_values: List[DashboardSQLQueryParameterValue]

class DashboardEvaluationRequest(BaseModel):
    dashboard_evaluation_sql_query: DashboardEvaluationSQLQuery
    chart_config: BoxChartConfig | ScatterChartConfig | PieChartConfig | LineChartConfig | HistogramChartConfig | BarChartConfig

class DashboardEvaluationResult(BaseModel):
    data_frame: PandasDataFrame
    figure: PlotlyFigure