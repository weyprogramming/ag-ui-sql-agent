from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

from plotly.express import bar, line, scatter, box, pie, histogram

from results.tool_results import PlotlyFigure


class PlotlyChartConfigBase(BaseModel):
    
    @abstractmethod
    def get_figure(self, dataframe) -> PlotlyFigure:
        pass
    
class BarChartConfig(PlotlyChartConfigBase):
    x: str | list[str] | None = Field(default=None, description="The column name(s) to use for the x-axis")
    y: str | list[str] | None = Field(default=None, description="The column name(s) to use for the y-axis")
    color: str | None = Field(default=None, description="Column name for color encoding")
    pattern_shape: str | None = Field(default=None, description="Column name for pattern shape encoding")
    facet_row: str | None = Field(default=None, description="Column name for facet rows")
    facet_col: str | None = Field(default=None, description="Column name for facet columns")
    facet_col_wrap: int = Field(default=0, description="Maximum number of facet columns")
    facet_row_spacing: float | None = Field(default=None, description="Spacing between facet rows")
    facet_col_spacing: float | None = Field(default=None, description="Spacing between facet columns")
    hover_name: str | None = Field(default=None, description="Column name for hover name")
    hover_data: list[str] | dict | None = Field(default=None, description="Columns to show in hover tooltip")
    custom_data: list[str] | None = Field(default=None, description="Custom data columns")
    text: str | None = Field(default=None, description="Column name for text labels")
    base: str | None = Field(default=None, description="Column name for base values")
    error_x: str | None = Field(default=None, description="Column name for x error bars")
    error_x_minus: str | None = Field(default=None, description="Column name for x error bars (minus)")
    error_y: str | None = Field(default=None, description="Column name for y error bars")
    error_y_minus: str | None = Field(default=None, description="Column name for y error bars (minus)")
    animation_frame: str | None = Field(default=None, description="Column name for animation frames")
    animation_group: str | None = Field(default=None, description="Column name for animation groups")
    category_orders: dict | None = Field(default=None, description="Dictionary of category orders")
    labels: dict | None = Field(default=None, description="Dictionary of axis labels")
    color_discrete_sequence: list[str] | None = Field(default=None, description="Sequence of discrete colors")
    color_discrete_map: dict | None = Field(default=None, description="Mapping of values to colors")
    color_continuous_scale: list | str | None = Field(default=None, description="Continuous color scale")
    pattern_shape_sequence: list[str] | None = Field(default=None, description="Sequence of pattern shapes")
    pattern_shape_map: dict | None = Field(default=None, description="Mapping of values to pattern shapes")
    range_color: list | None = Field(default=None, description="Range of color scale")
    color_continuous_midpoint: float | None = Field(default=None, description="Midpoint of color scale")
    opacity: float | None = Field(default=None, description="Opacity of bars")
    orientation: str | None = Field(default=None, description="Orientation ('v' or 'h')")
    barmode: str = Field(default="relative", description="Bar mode ('relative', 'group', 'overlay', 'stack')")
    log_x: bool = Field(default=False, description="Use log scale for x-axis")
    log_y: bool = Field(default=False, description="Use log scale for y-axis")
    range_x: list | None = Field(default=None, description="Range for x-axis")
    range_y: list | None = Field(default=None, description="Range for y-axis")
    text_auto: bool | str = Field(default=False, description="Automatic text labels")
    title: str | None = Field(default=None, description="Chart title")
    subtitle: str | None = Field(default=None, description="Chart subtitle")
    template: str | None = Field(default=None, description="Plotly template")
    width: int | None = Field(default=None, description="Chart width in pixels")
    height: int | None = Field(default=None, description="Chart height in pixels")
    
    def get_figure(self, dataframe) -> PlotlyFigure:
        fig = bar(
            dataframe,
            x=self.x,
            y=self.y,
            color=self.color,
            pattern_shape=self.pattern_shape,
            facet_row=self.facet_row,
            facet_col=self.facet_col,
            facet_col_wrap=self.facet_col_wrap,
            facet_row_spacing=self.facet_row_spacing,
            facet_col_spacing=self.facet_col_spacing,
            hover_name=self.hover_name,
            hover_data=self.hover_data,
            custom_data=self.custom_data,
            text=self.text,
            base=self.base,
            error_x=self.error_x,
            error_x_minus=self.error_x_minus,
            error_y=self.error_y,
            error_y_minus=self.error_y_minus,
            animation_frame=self.animation_frame,
            animation_group=self.animation_group,
            category_orders=self.category_orders,
            labels=self.labels,
            color_discrete_sequence=self.color_discrete_sequence,
            color_discrete_map=self.color_discrete_map,
            color_continuous_scale=self.color_continuous_scale,
            pattern_shape_sequence=self.pattern_shape_sequence,
            pattern_shape_map=self.pattern_shape_map,
            range_color=self.range_color,
            color_continuous_midpoint=self.color_continuous_midpoint,
            opacity=self.opacity,
            orientation=self.orientation,
            barmode=self.barmode,
            log_x=self.log_x,
            log_y=self.log_y,
            range_x=self.range_x,
            range_y=self.range_y,
            text_auto=self.text_auto,
            title=self.title,
            subtitle=self.subtitle,
            template=self.template,
            width=self.width,
            height=self.height
        )
        return PlotlyFigure.from_figure(fig)


class LineChartConfig(PlotlyChartConfigBase):
    x: str | list[str] | None = Field(default=None, description="The column name(s) to use for the x-axis")
    y: str | list[str] | None = Field(default=None, description="The column name(s) to use for the y-axis")
    line_group: str | None = Field(default=None, description="Column name for line grouping")
    color: str | None = Field(default=None, description="Column name for color encoding")
    line_dash: str | None = Field(default=None, description="Column name for line dash encoding")
    symbol: str | None = Field(default=None, description="Column name for symbol encoding")
    hover_name: str | None = Field(default=None, description="Column name for hover name")
    hover_data: list[str] | dict | None = Field(default=None, description="Columns to show in hover tooltip")
    custom_data: list[str] | None = Field(default=None, description="Custom data columns")
    text: str | None = Field(default=None, description="Column name for text labels")
    facet_row: str | None = Field(default=None, description="Column name for facet rows")
    facet_col: str | None = Field(default=None, description="Column name for facet columns")
    facet_col_wrap: int = Field(default=0, description="Maximum number of facet columns")
    facet_row_spacing: float | None = Field(default=None, description="Spacing between facet rows")
    facet_col_spacing: float | None = Field(default=None, description="Spacing between facet columns")
    error_x: str | None = Field(default=None, description="Column name for x error bars")
    error_x_minus: str | None = Field(default=None, description="Column name for x error bars (minus)")
    error_y: str | None = Field(default=None, description="Column name for y error bars")
    error_y_minus: str | None = Field(default=None, description="Column name for y error bars (minus)")
    animation_frame: str | None = Field(default=None, description="Column name for animation frames")
    animation_group: str | None = Field(default=None, description="Column name for animation groups")
    category_orders: dict | None = Field(default=None, description="Dictionary of category orders")
    labels: dict | None = Field(default=None, description="Dictionary of axis labels")
    orientation: str | None = Field(default=None, description="Orientation ('v' or 'h')")
    color_discrete_sequence: list[str] | None = Field(default=None, description="Sequence of discrete colors")
    color_discrete_map: dict | None = Field(default=None, description="Mapping of values to colors")
    line_dash_sequence: list[str] | None = Field(default=None, description="Sequence of line dash patterns")
    line_dash_map: dict | None = Field(default=None, description="Mapping of values to line dash patterns")
    symbol_sequence: list[str] | None = Field(default=None, description="Sequence of symbols")
    symbol_map: dict | None = Field(default=None, description="Mapping of values to symbols")
    markers: bool = Field(default=False, description="Show markers on lines")
    log_x: bool = Field(default=False, description="Use log scale for x-axis")
    log_y: bool = Field(default=False, description="Use log scale for y-axis")
    range_x: list | None = Field(default=None, description="Range for x-axis")
    range_y: list | None = Field(default=None, description="Range for y-axis")
    line_shape: str | None = Field(default=None, description="Line shape ('linear', 'spline', etc.)")
    render_mode: str = Field(default="auto", description="Render mode")
    title: str | None = Field(default=None, description="Chart title")
    subtitle: str | None = Field(default=None, description="Chart subtitle")
    template: str | None = Field(default=None, description="Plotly template")
    width: int | None = Field(default=None, description="Chart width in pixels")
    height: int | None = Field(default=None, description="Chart height in pixels")
    
    def get_figure(self, dataframe) -> PlotlyFigure:
        fig = line(
            dataframe,
            x=self.x,
            y=self.y,
            line_group=self.line_group,
            color=self.color,
            line_dash=self.line_dash,
            symbol=self.symbol,
            hover_name=self.hover_name,
            hover_data=self.hover_data,
            custom_data=self.custom_data,
            text=self.text,
            facet_row=self.facet_row,
            facet_col=self.facet_col,
            facet_col_wrap=self.facet_col_wrap,
            facet_row_spacing=self.facet_row_spacing,
            facet_col_spacing=self.facet_col_spacing,
            error_x=self.error_x,
            error_x_minus=self.error_x_minus,
            error_y=self.error_y,
            error_y_minus=self.error_y_minus,
            animation_frame=self.animation_frame,
            animation_group=self.animation_group,
            category_orders=self.category_orders,
            labels=self.labels,
            orientation=self.orientation,
            color_discrete_sequence=self.color_discrete_sequence,
            color_discrete_map=self.color_discrete_map,
            line_dash_sequence=self.line_dash_sequence,
            line_dash_map=self.line_dash_map,
            symbol_sequence=self.symbol_sequence,
            symbol_map=self.symbol_map,
            markers=self.markers,
            log_x=self.log_x,
            log_y=self.log_y,
            range_x=self.range_x,
            range_y=self.range_y,
            line_shape=self.line_shape,
            render_mode=self.render_mode,
            title=self.title,
            subtitle=self.subtitle,
            template=self.template,
            width=self.width,
            height=self.height
        )
        return PlotlyFigure.from_figure(fig)


class ScatterChartConfig(PlotlyChartConfigBase):
    x: str | list[str] | None = Field(default=None, description="The column name(s) to use for the x-axis")
    y: str | list[str] | None = Field(default=None, description="The column name(s) to use for the y-axis")
    color: str | None = Field(default=None, description="Column name for color encoding")
    symbol: str | None = Field(default=None, description="Column name for symbol encoding")
    size: str | None = Field(default=None, description="Column name for size encoding")
    hover_name: str | None = Field(default=None, description="Column name for hover name")
    hover_data: list[str] | dict | None = Field(default=None, description="Columns to show in hover tooltip")
    custom_data: list[str] | None = Field(default=None, description="Custom data columns")
    text: str | None = Field(default=None, description="Column name for text labels")
    facet_row: str | None = Field(default=None, description="Column name for facet rows")
    facet_col: str | None = Field(default=None, description="Column name for facet columns")
    facet_col_wrap: int = Field(default=0, description="Maximum number of facet columns")
    facet_row_spacing: float | None = Field(default=None, description="Spacing between facet rows")
    facet_col_spacing: float | None = Field(default=None, description="Spacing between facet columns")
    error_x: str | None = Field(default=None, description="Column name for x error bars")
    error_x_minus: str | None = Field(default=None, description="Column name for x error bars (minus)")
    error_y: str | None = Field(default=None, description="Column name for y error bars")
    error_y_minus: str | None = Field(default=None, description="Column name for y error bars (minus)")
    animation_frame: str | None = Field(default=None, description="Column name for animation frames")
    animation_group: str | None = Field(default=None, description="Column name for animation groups")
    category_orders: dict | None = Field(default=None, description="Dictionary of category orders")
    labels: dict | None = Field(default=None, description="Dictionary of axis labels")
    orientation: str | None = Field(default=None, description="Orientation ('v' or 'h')")
    color_discrete_sequence: list[str] | None = Field(default=None, description="Sequence of discrete colors")
    color_discrete_map: dict | None = Field(default=None, description="Mapping of values to colors")
    color_continuous_scale: list | str | None = Field(default=None, description="Continuous color scale")
    range_color: list | None = Field(default=None, description="Range of color scale")
    color_continuous_midpoint: float | None = Field(default=None, description="Midpoint of color scale")
    symbol_sequence: list[str] | None = Field(default=None, description="Sequence of symbols")
    symbol_map: dict | None = Field(default=None, description="Mapping of values to symbols")
    opacity: float | None = Field(default=None, description="Opacity of markers")
    size_max: int | None = Field(default=None, description="Maximum marker size")
    marginal_x: str | None = Field(default=None, description="Marginal plot type for x-axis")
    marginal_y: str | None = Field(default=None, description="Marginal plot type for y-axis")
    trendline: str | None = Field(default=None, description="Trendline type ('ols', 'lowess', etc.)")
    trendline_options: dict | None = Field(default=None, description="Options for trendline")
    trendline_color_override: str | None = Field(default=None, description="Color for trendline")
    trendline_scope: str = Field(default="trace", description="Scope for trendline")
    log_x: bool = Field(default=False, description="Use log scale for x-axis")
    log_y: bool = Field(default=False, description="Use log scale for y-axis")
    range_x: list | None = Field(default=None, description="Range for x-axis")
    range_y: list | None = Field(default=None, description="Range for y-axis")
    render_mode: str = Field(default="auto", description="Render mode")
    title: str | None = Field(default=None, description="Chart title")
    subtitle: str | None = Field(default=None, description="Chart subtitle")
    template: str | None = Field(default=None, description="Plotly template")
    width: int | None = Field(default=None, description="Chart width in pixels")
    height: int | None = Field(default=None, description="Chart height in pixels")
    
    def get_figure(self, dataframe) -> PlotlyFigure:
        fig = scatter(
            dataframe,
            x=self.x,
            y=self.y,
            color=self.color,
            symbol=self.symbol,
            size=self.size,
            hover_name=self.hover_name,
            hover_data=self.hover_data,
            custom_data=self.custom_data,
            text=self.text,
            facet_row=self.facet_row,
            facet_col=self.facet_col,
            facet_col_wrap=self.facet_col_wrap,
            facet_row_spacing=self.facet_row_spacing,
            facet_col_spacing=self.facet_col_spacing,
            error_x=self.error_x,
            error_x_minus=self.error_x_minus,
            error_y=self.error_y,
            error_y_minus=self.error_y_minus,
            animation_frame=self.animation_frame,
            animation_group=self.animation_group,
            category_orders=self.category_orders,
            labels=self.labels,
            orientation=self.orientation,
            color_discrete_sequence=self.color_discrete_sequence,
            color_discrete_map=self.color_discrete_map,
            color_continuous_scale=self.color_continuous_scale,
            range_color=self.range_color,
            color_continuous_midpoint=self.color_continuous_midpoint,
            symbol_sequence=self.symbol_sequence,
            symbol_map=self.symbol_map,
            opacity=self.opacity,
            size_max=self.size_max,
            marginal_x=self.marginal_x,
            marginal_y=self.marginal_y,
            trendline=self.trendline,
            trendline_options=self.trendline_options,
            trendline_color_override=self.trendline_color_override,
            trendline_scope=self.trendline_scope,
            log_x=self.log_x,
            log_y=self.log_y,
            range_x=self.range_x,
            range_y=self.range_y,
            render_mode=self.render_mode,
            title=self.title,
            subtitle=self.subtitle,
            template=self.template,
            width=self.width,
            height=self.height
        )
        return PlotlyFigure.from_figure(fig)


class BoxChartConfig(PlotlyChartConfigBase):
    x: str | None = Field(default=None, description="The column name to use for the x-axis")
    y: str | None = Field(default=None, description="The column name to use for the y-axis")
    color: str | None = Field(default=None, description="Column name for color encoding")
    facet_row: str | None = Field(default=None, description="Column name for facet rows")
    facet_col: str | None = Field(default=None, description="Column name for facet columns")
    facet_col_wrap: int = Field(default=0, description="Maximum number of facet columns")
    facet_row_spacing: float | None = Field(default=None, description="Spacing between facet rows")
    facet_col_spacing: float | None = Field(default=None, description="Spacing between facet columns")
    hover_name: str | None = Field(default=None, description="Column name for hover name")
    hover_data: list[str] | dict | None = Field(default=None, description="Columns to show in hover tooltip")
    custom_data: list[str] | None = Field(default=None, description="Custom data columns")
    animation_frame: str | None = Field(default=None, description="Column name for animation frames")
    animation_group: str | None = Field(default=None, description="Column name for animation groups")
    category_orders: dict | None = Field(default=None, description="Dictionary of category orders")
    labels: dict | None = Field(default=None, description="Dictionary of axis labels")
    color_discrete_sequence: list[str] | None = Field(default=None, description="Sequence of discrete colors")
    color_discrete_map: dict | None = Field(default=None, description="Mapping of values to colors")
    orientation: str | None = Field(default=None, description="Orientation ('v' or 'h')")
    boxmode: str | None = Field(default=None, description="Box mode ('group' or 'overlay')")
    log_x: bool = Field(default=False, description="Use log scale for x-axis")
    log_y: bool = Field(default=False, description="Use log scale for y-axis")
    range_x: list | None = Field(default=None, description="Range for x-axis")
    range_y: list | None = Field(default=None, description="Range for y-axis")
    points: str | None = Field(default=None, description="Show points ('all', 'outliers', 'suspectedoutliers', False)")
    notched: bool = Field(default=False, description="Show notched boxes")
    title: str | None = Field(default=None, description="Chart title")
    subtitle: str | None = Field(default=None, description="Chart subtitle")
    template: str | None = Field(default=None, description="Plotly template")
    width: int | None = Field(default=None, description="Chart width in pixels")
    height: int | None = Field(default=None, description="Chart height in pixels")
    
    def get_figure(self, dataframe) -> PlotlyFigure:
        fig = box(
            dataframe,
            x=self.x,
            y=self.y,
            color=self.color,
            facet_row=self.facet_row,
            facet_col=self.facet_col,
            facet_col_wrap=self.facet_col_wrap,
            facet_row_spacing=self.facet_row_spacing,
            facet_col_spacing=self.facet_col_spacing,
            hover_name=self.hover_name,
            hover_data=self.hover_data,
            custom_data=self.custom_data,
            animation_frame=self.animation_frame,
            animation_group=self.animation_group,
            category_orders=self.category_orders,
            labels=self.labels,
            color_discrete_sequence=self.color_discrete_sequence,
            color_discrete_map=self.color_discrete_map,
            orientation=self.orientation,
            boxmode=self.boxmode,
            log_x=self.log_x,
            log_y=self.log_y,
            range_x=self.range_x,
            range_y=self.range_y,
            points=self.points,
            notched=self.notched,
            title=self.title,
            subtitle=self.subtitle,
            template=self.template,
            width=self.width,
            height=self.height
        )
        return PlotlyFigure.from_figure(fig)


class PieChartConfig(PlotlyChartConfigBase):
    names: str | None = Field(default=None, description="Column name for sector names")
    values: str | None = Field(default=None, description="Column name for sector values")
    color: str | None = Field(default=None, description="Column name for color encoding")
    facet_row: str | None = Field(default=None, description="Column name for facet rows")
    facet_col: str | None = Field(default=None, description="Column name for facet columns")
    facet_col_wrap: int = Field(default=0, description="Maximum number of facet columns")
    facet_row_spacing: float | None = Field(default=None, description="Spacing between facet rows")
    facet_col_spacing: float | None = Field(default=None, description="Spacing between facet columns")
    color_discrete_sequence: list[str] | None = Field(default=None, description="Sequence of discrete colors")
    color_discrete_map: dict | None = Field(default=None, description="Mapping of values to colors")
    hover_name: str | None = Field(default=None, description="Column name for hover name")
    hover_data: list[str] | dict | None = Field(default=None, description="Columns to show in hover tooltip")
    custom_data: list[str] | None = Field(default=None, description="Custom data columns")
    category_orders: dict | None = Field(default=None, description="Dictionary of category orders")
    labels: dict | None = Field(default=None, description="Dictionary of labels")
    title: str | None = Field(default=None, description="Chart title")
    subtitle: str | None = Field(default=None, description="Chart subtitle")
    template: str | None = Field(default=None, description="Plotly template")
    width: int | None = Field(default=None, description="Chart width in pixels")
    height: int | None = Field(default=None, description="Chart height in pixels")
    opacity: float | None = Field(default=None, description="Opacity of sectors")
    hole: float | None = Field(default=None, description="Fraction of radius to cut out (for donut chart)")
    
    def get_figure(self, dataframe) -> PlotlyFigure:
        fig = pie(
            dataframe,
            names=self.names,
            values=self.values,
            color=self.color,
            facet_row=self.facet_row,
            facet_col=self.facet_col,
            facet_col_wrap=self.facet_col_wrap,
            facet_row_spacing=self.facet_row_spacing,
            facet_col_spacing=self.facet_col_spacing,
            color_discrete_sequence=self.color_discrete_sequence,
            color_discrete_map=self.color_discrete_map,
            hover_name=self.hover_name,
            hover_data=self.hover_data,
            custom_data=self.custom_data,
            category_orders=self.category_orders,
            labels=self.labels,
            title=self.title,
            subtitle=self.subtitle,
            template=self.template,
            width=self.width,
            height=self.height,
            opacity=self.opacity,
            hole=self.hole
        )
        return PlotlyFigure.from_figure(fig)


class HistogramChartConfig(PlotlyChartConfigBase):
    x: str | None = Field(default=None, description="The column name to use for the x-axis")
    y: str | None = Field(default=None, description="The column name to use for the y-axis")
    color: str | None = Field(default=None, description="Column name for color encoding")
    pattern_shape: str | None = Field(default=None, description="Column name for pattern shape encoding")
    facet_row: str | None = Field(default=None, description="Column name for facet rows")
    facet_col: str | None = Field(default=None, description="Column name for facet columns")
    facet_col_wrap: int = Field(default=0, description="Maximum number of facet columns")
    facet_row_spacing: float | None = Field(default=None, description="Spacing between facet rows")
    facet_col_spacing: float | None = Field(default=None, description="Spacing between facet columns")
    hover_name: str | None = Field(default=None, description="Column name for hover name")
    hover_data: list[str] | dict | None = Field(default=None, description="Columns to show in hover tooltip")
    animation_frame: str | None = Field(default=None, description="Column name for animation frames")
    animation_group: str | None = Field(default=None, description="Column name for animation groups")
    category_orders: dict | None = Field(default=None, description="Dictionary of category orders")
    labels: dict | None = Field(default=None, description="Dictionary of axis labels")
    color_discrete_sequence: list[str] | None = Field(default=None, description="Sequence of discrete colors")
    color_discrete_map: dict | None = Field(default=None, description="Mapping of values to colors")
    pattern_shape_sequence: list[str] | None = Field(default=None, description="Sequence of pattern shapes")
    pattern_shape_map: dict | None = Field(default=None, description="Mapping of values to pattern shapes")
    marginal: str | None = Field(default=None, description="Marginal plot type ('rug', 'box', 'violin', 'histogram')")
    opacity: float | None = Field(default=None, description="Opacity of bars")
    orientation: str | None = Field(default=None, description="Orientation ('v' or 'h')")
    barmode: str = Field(default="relative", description="Bar mode ('relative', 'group', 'overlay', 'stack')")
    barnorm: str | None = Field(default=None, description="Bar normalization ('fraction', 'percent')")
    histnorm: str | None = Field(default=None, description="Histogram normalization")
    log_x: bool = Field(default=False, description="Use log scale for x-axis")
    log_y: bool = Field(default=False, description="Use log scale for y-axis")
    range_x: list | None = Field(default=None, description="Range for x-axis")
    range_y: list | None = Field(default=None, description="Range for y-axis")
    histfunc: str | None = Field(default=None, description="Histogram function ('count', 'sum', 'avg', etc.)")
    cumulative: bool | None = Field(default=None, description="Show cumulative histogram")
    nbins: int | None = Field(default=None, description="Number of bins")
    text_auto: bool | str = Field(default=False, description="Automatic text labels")
    title: str | None = Field(default=None, description="Chart title")
    subtitle: str | None = Field(default=None, description="Chart subtitle")
    template: str | None = Field(default=None, description="Plotly template")
    width: int | None = Field(default=None, description="Chart width in pixels")
    height: int | None = Field(default=None, description="Chart height in pixels")
    
    def get_figure(self, dataframe) -> PlotlyFigure:
        fig = histogram(
            dataframe,
            x=self.x,
            y=self.y,
            color=self.color,
            pattern_shape=self.pattern_shape,
            facet_row=self.facet_row,
            facet_col=self.facet_col,
            facet_col_wrap=self.facet_col_wrap,
            facet_row_spacing=self.facet_row_spacing,
            facet_col_spacing=self.facet_col_spacing,
            hover_name=self.hover_name,
            hover_data=self.hover_data,
            animation_frame=self.animation_frame,
            animation_group=self.animation_group,
            category_orders=self.category_orders,
            labels=self.labels,
            color_discrete_sequence=self.color_discrete_sequence,
            color_discrete_map=self.color_discrete_map,
            pattern_shape_sequence=self.pattern_shape_sequence,
            pattern_shape_map=self.pattern_shape_map,
            marginal=self.marginal,
            opacity=self.opacity,
            orientation=self.orientation,
            barmode=self.barmode,
            barnorm=self.barnorm,
            histnorm=self.histnorm,
            log_x=self.log_x,
            log_y=self.log_y,
            range_x=self.range_x,
            range_y=self.range_y,
            histfunc=self.histfunc,
            cumulative=self.cumulative,
            nbins=self.nbins,
            text_auto=self.text_auto,
            title=self.title,
            subtitle=self.subtitle,
            template=self.template,
            width=self.width,
            height=self.height
        )
        return PlotlyFigure.from_figure(fig)