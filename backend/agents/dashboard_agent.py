import asyncio

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

from textwrap import dedent

from pydantic_ai import Agent, RunContext, ModelRetry
from pydantic_ai.ag_ui import StateDeps

from ag_ui.core import StateSnapshotEvent, EventType

from pandas import DataFrame

from states.dashboard_state import State, DashboardState
from results.dashboard_config_results import DashboardConfig
from results.tool_results import PandasDataFrame

dashboard_agent = Agent(deps_type=StateDeps[State], model="openai:gpt-5-nano")

@dashboard_agent.instructions
def dashboard_instructions(ctx: RunContext[State]) -> str:
    return dedent(f"""
        You are a data scientist who should create a dashboard to visualize data from a SQL database.
        You have to generate a parametrized SQL query to get the data for the dashboard.
        The database looks the following:
        <database>
        {ctx.deps.sql_dependency.get_prompt()}
        </database>
        Use the `execute_sql_query` function to explore the database and test sql queries.
        This may be useful to explore the database and test your SQL queries.
        Use the create_dashboard_config tool to create the dashboard configuration.
    """)

@dashboard_agent.tool(retries=5)
async def execute_sql_query(
    ctx: RunContext[State], query: str, n: int = 20
) -> PandasDataFrame:
    """
    Execute a SQL query on the connected database and return a JSON representation of the resulting dataframe.
    
    The query should be a valid SQL query. Write the query as efficiently as possible to avoid long execution times.
    The n parameter specifies the number of rows to return (default is 20).
    
    Use this tool to explore the database and test your SQL queries.
    """
    
    async def execute_query():
        with ThreadPoolExecutor() as executor:
            return await asyncio.get_event_loop().run_in_executor(
                executor,
                ctx.deps.sql_dependency.get_dataframe_from_query,
                query
            )

    try:
        result_df = await asyncio.wait_for(execute_query(), timeout=10)
        
        result = PandasDataFrame.from_dataframe(result_df.head(n))

                
        
    except asyncio.TimeoutError:
        raise ModelRetry("SQL query execution timed out after 10 seconds")
    
    except Exception as e:
        raise ModelRetry(f"Error while executing SQL query: {str(e)}")
    
    if result_df.empty:
        raise ModelRetry("The resulting DataFrame is empty. You may wanna check your filters.")
    
    return result


@dashboard_agent.tool(retries=5)
async def save_dashboard_config(
    ctx: RunContext[State],
    dashboard_config: DashboardConfig
) -> StateSnapshotEvent:
    """
    Save the dashboard configuration.
    """
    
    test_df = ctx.deps.sql_dependency.test_dashboard_sql_query(dashboard_config.dashboard_sql_query)
    test_figure = dashboard_config.chart_config.get_figure(DataFrame(**test_df.model_dump()))
    
    state = DashboardState(
        dashboard_config=dashboard_config,
        test_dateframe=test_df,
        test_figure=test_figure
    )
    
    state_snapshot_event = StateSnapshotEvent(
        snapshot=state,
        type=EventType.STATE_SNAPSHOT
    )
    
    return state_snapshot_event