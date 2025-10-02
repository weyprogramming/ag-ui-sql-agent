from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

SQLQueryParameterType = Literal["string", "int", "float", "date", "boolean"]

class DashboardConfig(BaseModel):
    pass

class DashboardSQLQuery(BaseModel):
    pass

class DashboardSQLQueryParameter(BaseModel):
    pass

class DashboardPlotlyChartConfig(BaseModel):
    pass