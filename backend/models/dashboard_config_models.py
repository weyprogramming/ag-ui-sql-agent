from __future__ import annotations

from typing import Literal, List

from aredis_om import EmbeddedJsonModel, JsonModel

from results.dashboard_config_results import *


class DashboardConfigModel(JsonModel, DashboardConfig):
    pass

class DashboardSQLQueryModel(EmbeddedJsonModel, DashboardSQLQuery):
    pass

class DashboardSQLQueryParameterModel(EmbeddedJsonModel, DashboardSQLQueryParameter):
    pass

class DashboardPlotlyChartConfigModel(EmbeddedJsonModel, DashboardPlotlyChartConfig):
    pass