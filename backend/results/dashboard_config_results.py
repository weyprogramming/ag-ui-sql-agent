from __future__ import annotations

from typing import Literal, List

from pydantic import BaseModel, Field

SQLQueryParameterType = Literal["string", "int", "float", "date", "boolean"]

class DashboardConfig(BaseModel):
    title: str
    dashboard_sql_query: DashboardSQLQuery
    #plotly_chart_config: DashboardPlotlyChartConfig

class DashboardSQLQuery(BaseModel):
    parametrized_query: str = Field(
        description="A parametrized SQL query with parameters in curly braces, e.g. SELECT * FROM table WHERE column = {parameter}"
    )
    dashboard_sql_query_parameters: List[DashboardSQLQueryParameter] = Field(
        description="A list of parameters used in the parametrized_query"
    )

class DashboardSQLQueryParameter(BaseModel):
    name: str
    type: SQLQueryParameterType

class DashboardPlotlyChartConfig(BaseModel):
    pass