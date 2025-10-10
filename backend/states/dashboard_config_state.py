from datetime import date, datetime, time
from typing import List

from pydantic import BaseModel


from results.plotly_chart_config_results import BoxChartConfig, ScatterChartConfig, PieChartConfig, LineChartConfig, HistogramChartConfig, BarChartConfig
from results.tool_results import PandasDataFrame, PlotlyFigure
from results.dashboard_config_results import DashboardSQLQueryResult
from schemas.dashboard_evaluation import DashboardSQLQueryParameterValue
from models.sql_dependency_model import SQLBaseDependencyModel



class DashboardSQLQueryState(DashboardSQLQueryResult):
    sql_dependency_id: str
    
    async def get_sql_dependency(self) -> SQLBaseDependencyModel:
        return await SQLBaseDependencyModel.get(self.sql_dependency_id)


    def evaluate_query(self, parameter_values: List[DashboardSQLQueryParameterValue]) -> str:
        evaluated_query = self.parametrized_query
        
        for param in parameter_values:
            placeholder = "{" + param.name + "}"
            
            if placeholder not in evaluated_query:
                raise ValueError(f"Parameter '{param.name}' not found in query")
            
            if isinstance(param.value, str):
                value_str = f"'{param.value}'"
            elif isinstance(param.value, bool):
                value_str = 'TRUE' if param.value else 'FALSE'
            elif isinstance(param.value, (datetime, date, time)):
                value_str = f"'{param.value.isoformat()}'"
            else:
                value_str = str(param.value)
            
            evaluated_query = evaluated_query.replace(placeholder, value_str)
        
        return evaluated_query
    
    
    async def execute_query(self, parameter_values: List[DashboardSQLQueryParameterValue]) -> PandasDataFrame:
        sql_dependency = await self.get_sql_dependency()
        query = self.evaluate_query(parameter_values)
        return PandasDataFrame.from_dataframe(sql_dependency.get_dataframe_from_query(query))


class DashboardConfigState(BaseModel):
    dashboard_sql_query: DashboardSQLQueryState | None = None
    chart_config: BoxChartConfig | ScatterChartConfig | PieChartConfig | LineChartConfig | HistogramChartConfig | BarChartConfig | None = None