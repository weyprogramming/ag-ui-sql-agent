import asyncio

from uuid import UUID

from concurrent.futures import TimeoutError as FuturesTimeoutError

from textwrap import dedent

from pydantic_ai import Agent, RunContext, ModelRetry, ToolReturn, ToolDefinition
from pydantic_ai.ag_ui import StateDeps

from ag_ui.core import StateSnapshotEvent, EventType

from states.dashboard_state import DashboardState
from states.dashboard_config_state import DashboardSQLQueryState
from results.dashboard_config_results import DashboardSQLQueryResult
from results.tool_results import PandasDataFrame, PlotlyFigure
from results.plotly_chart_config_results import BoxChartConfig, ScatterChartConfig, PieChartConfig, LineChartConfig, HistogramChartConfig, BarChartConfig

dashboard_agent = Agent(deps_type=StateDeps[DashboardState], model="anthropic:claude-sonnet-4-0")

@dashboard_agent.instructions
async def dashboard_instructions(ctx: RunContext[StateDeps[DashboardState]]) -> str:

    sql_dependency = await ctx.deps.state.get_sql_dependency()
       
    return dedent(f"""
        You are an AI agent that helps create dashboard configurations based on a connected SQL database.
        You want to create a dashboard configuration based on the user's requirements.
        You want to help the user to create an insightful dashboard.
        Clarify the user's requirements if necessary.
        If there are several ways to compute a metric the user asked for, explain the options and ask the user to choose one.
        Make suggestions for dashboards based on the data available in the database.
        The database has the following tables available:
        <database>
        {sql_dependency.get_instruction_prompt()}
        </database>
        {sql_dependency.get_dialect_prompt()}
        You can create one SQL query to fetch all the data you need.
        Then you can create multiple figures based on the dataframe returned by the SQL query.
        You should iterate with the user until they are satisfied with the dashboard configuration.
        Use the tools available to you to explore the database, execute SQL queries and save the dashboard configuration.
        ALWAYS FOLLOW THE FOLLOWING STEPS IN ORDER:
        1. Clarify the user's requirements to translate them into a parametrized SQL query and figure configurations.
        2. Create a parametrized SQL query that computes the metrics the user asked for.
        3. Now you can create figure configurations based on the dataframe returned by the SQL query.
        4. Communicate with the user, suggest improvements and apply changes. 
    """)

@dashboard_agent.tool()
async def explore_database_table(
    ctx: RunContext[StateDeps[DashboardState]],
    table_id: UUID
) -> ToolReturn:
    """
    Explore the structure of a database table.
    Returns the table name, comment and columns with their names, types and comments.
    """
    
    sql_dependency = await ctx.deps.state.get_sql_dependency()
    
    table = sql_dependency.get_table_by_id(table_id)
    
    if table is None:
        raise ModelRetry(f"Table with id {table_id} not found in the database")
    
    return ToolReturn(
        return_value=table.get_dict(),
        metadata=[
            StateSnapshotEvent(
                type=EventType.STATE_SNAPSHOT,
                snapshot=DashboardState.model_validate(ctx.deps.state)
            )
        ]
    )
    

@dashboard_agent.tool()
async def get_database_table_content(
    ctx: RunContext[StateDeps[DashboardState]],
    table_id: UUID,
    n: int = 5
) -> ToolReturn:
    """
    Get a sample of the content of a database table.
    Returns the first n rows of the table as a JSON representation of a dataframe.
    Use this tool if you want to see values in the table to better understand the data.
    """
    
    sql_dependency = await ctx.deps.state.get_sql_dependency()
    
    table = sql_dependency.get_table_by_id(table_id)
    
    if sql_dependency.connection_params.type == "postgres":
        sql_query = f"SELECT * FROM {table.table_name} LIMIT {n}"
    
    elif sql_dependency.connection_params.type == "mysql":
        sql_query = f"SELECT * FROM {table.table_name} LIMIT {n}"
        
    elif sql_dependency.connection_params.type == "mssql":
        sql_query = f"SELECT TOP {n} * FROM {table.table_name}"

    if table is None:
        raise ModelRetry(f"Table with id {table_id} not found in the database")
    
    try:
        df = await asyncio.to_thread(sql_dependency.get_dataframe_from_query, sql_query)
        result = PandasDataFrame.from_dataframe(df)
        
    except Exception as exc:
        raise ModelRetry(f"Error while fetching table content: {exc}") from exc
    
    return ToolReturn(
        return_value=result.model_dump_json(),
        metadata=[
            StateSnapshotEvent(
                type=EventType.STATE_SNAPSHOT,
                snapshot=DashboardState.model_validate(ctx.deps.state)
            )
        ]
    )
    

async def prepare_execute_sql_query(
    ctx: RunContext[StateDeps[DashboardState]],
    tool_def: ToolDefinition
) -> ToolDefinition | None:
    
    if ctx.deps.state.selected_sql_dependency_id is None:
        return None
    
    sql_dependency = await ctx.deps.state.get_sql_dependency()
    
    tool_def.description = dedent(f"""
        Execute a SQL query on the connected database and return a JSON representation of the resulting dataframe.
        The query should be a valid SQL query. Write the query as efficiently as possible to avoid long execution times.
        The n parameter specifies the number of rows to return (default is 20).
        IMPORTANT: Don't use this tool if other tools are sufficient. Write your SQL queries as efficiently as possible to avoid long execution times.
        {sql_dependency.get_dialect_prompt()}
    """)

    return tool_def
    


@dashboard_agent.tool(retries=5)
async def execute_sql_query(
    ctx: RunContext[StateDeps[DashboardState]], query: str, n: int = 20
) -> ToolReturn:
    """
    Execute a SQL query on the connected database and return a JSON representation of the resulting dataframe.
    
    The query should be a valid SQL query. Write the query as efficiently as possible to avoid long execution times.
    The n parameter specifies the number of rows to return (default is 20).
    
    IMPORTANT: Write your SQL queries as efficiently as possible to avoid long execution times.
    """
    
    sql_dependency = await ctx.deps.state.get_sql_dependency()
    
    try:
        result_df = await asyncio.wait_for(
            asyncio.to_thread(sql_dependency.get_dataframe_from_query, query),
            timeout=180
        )
        result = PandasDataFrame.from_dataframe(result_df.head(n=n))

        
    except asyncio.TimeoutError as exc:
        raise ModelRetry("SQL query execution timed out after 30 seconds") from exc

    except Exception as exc:
        raise ModelRetry(f"Error while executing SQL query: {exc}") from exc
    
    return ToolReturn(
        return_value=result.model_dump_json(),
        metadata=[
            StateSnapshotEvent(
                type=EventType.STATE_SNAPSHOT,
                snapshot=DashboardState.model_validate(ctx.deps.state)
            )
        ]
    )
    
    
async def prepare_save_dashboard_sql_query(
    ctx: RunContext[StateDeps[DashboardState]],
    tool_def: ToolDefinition
) -> ToolDefinition | None:
    
    if ctx.deps.state.selected_sql_dependency_id is None:
        return None
    
    sql_dependency = await ctx.deps.state.get_sql_dependency()
    
    tool_def.description = dedent(f"""
        Saves the parametrized SQL query for the dashboard.
        Returns a dataframe with the result of the query with default values against the chosen database.
        You may want to choose default values that return a meaningful result.
        {sql_dependency.get_dialect_prompt()}
    """)

    return tool_def


@dashboard_agent.tool(retries=5)
async def save_dashboard_sql_query(
    ctx: RunContext[StateDeps[DashboardState]],
    dashboard_sql_query: DashboardSQLQueryResult
) -> ToolReturn:

    dashboard_sql_query = DashboardSQLQueryState(
        sql_dependency_id=ctx.deps.state.selected_sql_dependency_id,
        parametrized_query=dashboard_sql_query.parametrized_query,
        dashboard_sql_query_parameters=dashboard_sql_query.dashboard_sql_query_parameters
    )
    
    ctx.deps.state.dashboard_config.dashboard_sql_query = dashboard_sql_query
    
    try:
        await ctx.deps.state.evaluate_default_dataframe()
        
    except Exception as exc:
        raise ModelRetry(f"Error while executing test SQL query: {exc}") from exc
    
    return ToolReturn(
        return_value=ctx.deps.state.default_dataframe.head(),
        metadata=[
            StateSnapshotEvent(
                type=EventType.STATE_SNAPSHOT,
                snapshot=DashboardState.model_validate(ctx.deps.state)
            )
        ]
    )
    
async def prepare_save_dashboard_figure_config(
    ctx: RunContext[StateDeps[DashboardState]],
    tool_def: ToolDefinition
) -> ToolDefinition | None:
    
    if ctx.deps.state.dashboard_config.dashboard_sql_query is None:
        return None
    
    if ctx.deps.state.default_dataframe is None:
        return None
    
    tool_def.description = dedent(f"""
        You have the following dataframe available to create a plotly Figure from:
        {ctx.deps.state.default_dataframe.model_dump_json(indent=2)}
        The input to this function has to be an object which gets passed to a `plotly.express` function.
        For example, `LineChartConfig` gets passed to `plotly.express.line`.
        Returns a JSON representation of the created figure with the default dataframe.
    """)

    return tool_def

@dashboard_agent.tool(retries=5, prepare=prepare_save_dashboard_figure_config)
async def add_dashboard_figure_config(
    ctx: RunContext[StateDeps[DashboardState]],
    figure_config: BoxChartConfig | ScatterChartConfig | PieChartConfig | LineChartConfig | HistogramChartConfig | BarChartConfig
) -> ToolReturn:
    
    if ctx.deps.state.dashboard_config.dashboard_sql_query is None:
        raise ModelRetry("No SQL query configured for the dashboard")
    
    ctx.deps.state.dashboard_config.figure_configs.append(figure_config)
    ctx.deps.state.evaluate_default_figures()
    
    return ToolReturn(
        return_value=ctx.deps.state.default_figures[-1],
        metadata=[
            StateSnapshotEvent(
                type=EventType.STATE_SNAPSHOT,
                snapshot=DashboardState.model_validate(ctx.deps.state)
            )
        ]
    )
    
    
async def prepare_remove_dashboard_figure_config(
    ctx: RunContext[StateDeps[DashboardState]],
    tool_def: ToolDefinition
) -> ToolDefinition | None:
    
    if not ctx.deps.state.dashboard_config.figure_configs or len(ctx.deps.state.dashboard_config.figure_configs) == 0:
        return None
    
    tool_def.description = dedent(f"""
        You have the following figure configurations in the dashboard:
        {[fig.model_dump_json(indent=2) for fig in ctx.deps.state.dashboard_config.figure_configs]}
        The input to this function has to be the index of the figure configuration to remove (0-based).
        Returns a message if the figure configuration was removed successfully.
    """)

    return tool_def


@dashboard_agent.tool(retries=5, prepare=prepare_remove_dashboard_figure_config)
async def remove_dashboard_figure_config(
    ctx: RunContext[StateDeps[DashboardState]],
    index: int
) -> ToolReturn:
    
    if not ctx.deps.state.dashboard_config.figure_configs:
        raise ModelRetry("No figure configurations in the dashboard")
    
    if index < 0 or index >= len(ctx.deps.state.dashboard_config.figure_configs):
        raise ModelRetry(f"Index {index} is out of bounds for figure configurations")
    
    ctx.deps.state.dashboard_config.figure_configs.pop(index)
    ctx.deps.state.evaluate_default_figures()
    
    return ToolReturn(
        return_value=[fig.model_dump_json(indent=2) for fig in ctx.deps.state.default_figures],
        metadata=[
            StateSnapshotEvent(
                type=EventType.STATE_SNAPSHOT,
                snapshot=DashboardState.model_validate(ctx.deps.state)
            )
        ]
    )
    
    
async def prepare_edit_dashboard_figure_config(
    ctx: RunContext[StateDeps[DashboardState]],
    tool_def: ToolDefinition
) -> ToolDefinition | None:
    
    if not ctx.deps.state.dashboard_config.figure_configs or len(ctx.deps.state.dashboard_config.figure_configs) == 0:
        return None
    
    tool_def.description = dedent(f"""
        You have the following figure configurations in the dashboard:
        { [fig.model_dump_json(indent=2) for fig in ctx.deps.state.dashboard_config.figure_configs] }
        The input to this function has to be an object with two fields:
        - index: The index of the figure configuration to edit (0-based).
        - figure_config: The new figure configuration to replace the old one.
        Returns a list of JSON representations of the current figures in the dashboard after editing the figure configuration.
    """)

    return tool_def


@dashboard_agent.tool(retries=5, prepare=prepare_edit_dashboard_figure_config)
async def edit_dashboard_figure_config(
    ctx: RunContext[StateDeps[DashboardState]],
    index: int,
    figure_config: BoxChartConfig | ScatterChartConfig | PieChartConfig | LineChartConfig | HistogramChartConfig | BarChartConfig
) -> ToolReturn:
    
    if not ctx.deps.state.dashboard_config.figure_configs:
        raise ModelRetry("No figure configurations in the dashboard")
    
    if index < 0 or index >= len(ctx.deps.state.dashboard_config.figure_configs):
        raise ModelRetry(f"Index {index} is out of bounds for figure configurations")
    
    ctx.deps.state.dashboard_config.figure_configs[index] = figure_config
    ctx.deps.state.evaluate_default_figures()
    
    return ToolReturn(
        return_value=[fig.model_dump_json(indent=2) for fig in ctx.deps.state.default_figures],
        metadata=[
            StateSnapshotEvent(
                type=EventType.STATE_SNAPSHOT,
                snapshot=DashboardState.model_validate(ctx.deps.state)
            )
        ]
    )