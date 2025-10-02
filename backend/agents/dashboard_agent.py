import asyncio

from concurrent.futures import ThreadPoolExecutor

from textwrap import dedent

from pydantic_ai import Agent, RunContext, ModelRetry
from pydantic_ai.ag_ui import StateDeps

from ag_ui.core import StateSnapshotEvent, EventType

from pandas import DataFrame

from states.dashboard_state import DashboardState
from results.dashboard_config_results import DashboardConfig
from results.tool_results import PandasDataFrame

dashboard_agent = Agent(deps_type=StateDeps[DashboardState], model="anthropic:claude-sonnet-4-0")

@dashboard_agent.instructions
def dashboard_instructions(ctx: RunContext[DashboardState]) -> str:
    return dedent(f"""
        You are a data scientist who should create a dashboard to visualize data from a SQL database.
        You want to chat with the user to understand what they want to visualize.
        You have to generate a parametrized SQL query to get the data for the dashboard.
        The database looks the following:
        <database>
        {ctx.deps.sql_dependency.get_prompt()}
        </database>
        You can use the execute_sql_query tool to run SQL queries against the database.
        This may be useful to explore the database and test your SQL queries.
        Use the create_dashboard_config tool to create the dashboard configuration.
    """)

@dashboard_agent.tool(retries=5)
async def execute_sql_query(
    ctx: RunContext[DashboardState], query: str
) -> PandasDataFrame:
    """
    Execute a SQL query on the connected database and return a JSON representation of the resulting dataframe.
    """
    
    async def execute_query():
        with ThreadPoolExecutor() as executor:
            return await asyncio.get_event_loop().run_in_executor(
                executor,
                ctx.deps.sql_dependency.get_dataframe_from_query,
                query
            )

    try:
        result_df = await asyncio.wait_for(execute_query(), timeout=300)
        result = PandasDataFrame.model_validate(result_df.to_dict(orient="split"))             
        
    except asyncio.TimeoutError:
        raise ModelRetry("SQL query execution timed out after 300 seconds")
    
    except Exception as e:
        raise ModelRetry(f"Error while executing SQL query: {str(e)}")
    
    if result_df.empty:
        raise ModelRetry("The resulting DataFrame is empty. You may wanna check your filters.")
    
    return result


@dashboard_agent.tool_plain
async def save_dashboard_config(
    dashboard_config: DashboardConfig
) -> StateSnapshotEvent:
    """
    Save the dashboard configuration.
    """
    
    state_snapshot_event = StateSnapshotEvent(
        snapshot=DashboardConfig.model_validate(dashboard_config),
        type=EventType.STATE_SNAPSHOT
    )
    
    return state_snapshot_event