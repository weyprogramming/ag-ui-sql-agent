from typing import Literal, List

from datetime import datetime, date, time

from pydantic import BaseModel, Field, model_validator

from results.tool_results import PandasDataFrame, PlotlyFigure
from results.plotly_chart_config_results import BarChartConfig, LineChartConfig, PieChartConfig, ScatterChartConfig, HistogramChartConfig, BoxChartConfig


SQLQueryParameterType = Literal["str", "int", "float", "date", "bool", "datetime", "time"]

class DashboardSQLQueryParameter(BaseModel):
    name: str = Field(
        description="The name of the parameter, e.g. 'parameter' for {parameter}"
    )
    type: SQLQueryParameterType = Field(
        description="The type of the parameter, e.g. 'str', 'int', 'float', 'date', 'bool', 'datetime', or 'time'"
    )
    default_value: str | int | float | date | bool | datetime | time = Field(
        description="An example value for the parameter, e.g. 'example' for a str parameter"
    )

class DashboardSQLQueryResult(BaseModel):
    parametrized_query: str = Field(
        description="A parametrized SQL query with parameters in curly braces, e.g. SELECT * FROM table WHERE column = {parameter}"
    )
    dashboard_sql_query_parameters: List[DashboardSQLQueryParameter] = Field(
        description="A list of parameters used in the parametrized_query"
    )
    
    