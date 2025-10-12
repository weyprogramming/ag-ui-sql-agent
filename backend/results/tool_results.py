from __future__ import annotations

import json

from typing import List, Any, Dict

from pydantic import BaseModel

from pandas import DataFrame
from plotly.graph_objects import Figure

class SQLQueryResult(BaseModel):
    query: str
    result: PandasDataFrame

class PandasDataFrame(BaseModel):
    data: List[List[Any]]
    columns: List[str]
    index: List[Any] | None = None
    
    @classmethod
    def from_dataframe(cls, df: DataFrame) -> PandasDataFrame:
        return cls(
            data=df.values.tolist(),
            columns=df.columns.tolist(),
            index=df.index.tolist() if df.index is not None else None
        )
        
    def to_dataframe(self) -> DataFrame:
        return DataFrame(**self.model_dump())
    
class PlotlyFigure(BaseModel):
    data: List[Dict]
    layout: Dict[str, Any] | None = None
    config: Dict[str, Any] | None = None
    
    @classmethod
    def from_figure(cls, fig: Figure) -> PlotlyFigure:
        return cls(
            **json.loads(fig.to_json())
        )
        
    def to_figure(self) -> Figure:
        return Figure(**self.model_dump())