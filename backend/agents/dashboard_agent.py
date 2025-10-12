import asyncio

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

from textwrap import dedent

from pydantic_ai import Agent, RunContext, ModelRetry, ToolReturn
from pydantic_ai.ag_ui import StateDeps

from ag_ui.core import StateSnapshotEvent, EventType

from pandas import DataFrame


from states.dashboard_state import DashboardState
from states.dashboard_config_state import DashboardConfigState, DashboardSQLQueryState
from results.dashboard_config_results import DashboardSQLQueryResult
from results.tool_results import PandasDataFrame, PlotlyFigure
from results.plotly_chart_config_results import BoxChartConfig, ScatterChartConfig, PieChartConfig, LineChartConfig, HistogramChartConfig, BarChartConfig

dashboard_agent = Agent(deps_type=StateDeps[DashboardState], model="anthropic:claude-sonnet-4-0")

@dashboard_agent.instructions
async def dashboard_instructions(ctx: RunContext[StateDeps[DashboardState]]) -> str:
    
    sql_dependency = await ctx.deps.state.get_sql_dependency()
       
    return dedent(f"""
        You are a data scientist who should create a dashboard to visualize data from a SQL database.
        You have to generate a parametrized SQL query to get the data for the dashboard.
        The database looks the following:
        <database>
        {sql_dependency.get_prompt()}
        </database>
        Use the `execute_sql_query` function to explore the database and test sql queries.
        This may be useful to explore the database and test your SQL queries.
        Use the create_dashboard_config tool to create the dashboard configuration.
    """)

@dashboard_agent.tool(retries=5)
async def execute_sql_query(
    ctx: RunContext[StateDeps[DashboardState]], query: str, n: int = 20
) -> PandasDataFrame:
    """
    Execute a SQL query on the connected database and return a JSON representation of the resulting dataframe.
    
    The query should be a valid SQL query. Write the query as efficiently as possible to avoid long execution times.
    The n parameter specifies the number of rows to return (default is 20).
    
    Use this tool to explore the database and test your SQL queries.
    """
    
    sql_dependency = await ctx.deps.state.get_sql_dependency()
    
    async def execute_query():
        with ThreadPoolExecutor() as executor:
            return await asyncio.get_event_loop().run_in_executor(
                executor,
                sql_dependency.get_dataframe_from_query,
                query
            )

    try:
        result_df = await asyncio.wait_for(execute_query(), timeout=10)
        
        result = PandasDataFrame.from_dataframe(result_df.head(n))

                
        
    except asyncio.TimeoutError as exc:
        raise ModelRetry("SQL query execution timed out after 10 seconds") from exc

    except Exception as exc:
        raise ModelRetry(f"Error while executing SQL query: {exc}") from exc
    
    return result


@dashboard_agent.tool(retries=5)
async def save_dashboard_sql_query(
    ctx: RunContext[StateDeps[DashboardState]],
    dashboard_sql_query: DashboardSQLQueryResult
) -> StateSnapshotEvent:
    """
    Saves the parametrized SQL query for the dashboard.
    Returns a dataframe with the result of the query with default values against the chosen database.
    """


    dashboard_sql_query = DashboardSQLQueryState(
        sql_dependency_id=ctx.deps.state.selected_sql_dependency_id,
        parametrized_query=dashboard_sql_query.parametrized_query,
        dashboard_sql_query_parameters=dashboard_sql_query.dashboard_sql_query_parameters
    )
    
    ctx.deps.state.dashboard_config.dashboard_sql_query = dashboard_sql_query
    
    try:
        test_dataframe = await ctx.deps.state.evaluate_test_dataframe()
        
    except Exception as exc:
        raise ModelRetry(f"Error while executing test SQL query: {exc}") from exc
    
    ctx.deps.state.test_dataframe = test_dataframe
    
    return ToolReturn(
        return_value=ctx.deps.state.test_dataframe,
        metadata=[
            StateSnapshotEvent(
                type=EventType.STATE_SNAPSHOT,
                snapshot=DashboardState.model_validate(ctx.deps.state)
            )
        ]
    )
    
@dashboard_agent.tool(retries=5)
async def create_dashboard_config(
    ctx: RunContext[StateDeps[DashboardState]],
    chart_config: BoxChartConfig | ScatterChartConfig | PieChartConfig | LineChartConfig | HistogramChartConfig | BarChartConfig
) -> StateSnapshotEvent:
    """
    Saves the chart configuration for the dashboard.
    Returns the updated dashboard configuration state.
    """
    
    if ctx.deps.state.dashboard_config.dashboard_sql_query is None:
        raise ModelRetry("No SQL query configured for the dashboard")
    
    ctx.deps.state.dashboard_config.chart_config = chart_config
    ctx.deps.state.test_figure = chart_config.get_figure(
        dataframe=ctx.deps.state.test_dataframe.to_dataframe()
    )
    
    return ToolReturn(
        return_value=ctx.deps.state.dashboard_config,
        metadata=[
            StateSnapshotEvent(
                type=EventType.STATE_SNAPSHOT,
                snapshot=DashboardState.model_validate(ctx.deps.state)
            )
        ]
    )