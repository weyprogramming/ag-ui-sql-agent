from __future__ import annotations

from typing import Literal, List

from aredis_om import EmbeddedJsonModel, JsonModel

from results.dashboard_config_results import DashboardConfig

class DashboardConfigModel(JsonModel, DashboardConfig):
    pass