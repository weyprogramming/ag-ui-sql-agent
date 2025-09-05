import asyncio, json

from concurrent.futures import ThreadPoolExecutor

from pydantic_ai import Agent, RunContext, ModelRetry
from pydantic_ai.tools import ToolDefinition, Tool
from pydantic_ai.messages import ToolReturn
from pydantic_ai.ag_ui import StateDeps

from textwrap import dedent

from plotly.graph_objects import Figure

from state import State, SQLType
from result import PandasDataFrame, PlotlyFigure, SQLQueryResult

from utils import get_plotly_environment



agent = Agent("openai:gpt-4o", deps_type=StateDeps[State])

@agent.instructions
def instructions(ctx: RunContext[State]) -> str:
    return f"""
        You are a data analysis agent.
        You are working with a non technical user to help them analyze their data.
        If the requirements are not clear, ask clarifying questions.
        If there are serveral ways to solve a problem, explain the options and their pros and cons to the user.
        For every step you make, explain it with non technical terms to the user.
        Reply in the user's language.
    """

async def prepare_sql_tool(
    ctx: RunContext[State], tool_def: ToolDefinition
) -> ToolDefinition | None:
    
    if ctx.deps.sql_dependency is None:
        return None
    
    if ctx.deps.sql_dependency.connection_params.type == SQLType.MSSQL:
            dialect_string = "You have to use the Microsoft SQL Server Dialect. For example, use 'TOP' instead of 'LIMIT.'"
            
    elif ctx.deps.sql_dependency.connection_params.type == SQLType.MYSQL:
            dialect_string = "You have to use the MySQL Dialect."
            
    elif ctx.deps.sql_dependency.connection_params.type == SQLType.POSTGRES:
            dialect_string = "You have to use the PostgreSQL Dialect."
            
    elif ctx.deps.sql_dependency.connection_params.type == SQLType.SQLITE:
            dialect_string = "You have to use the SQLite Dialect."
            
    else:
        dialect_string = None
    
    tool_description = dedent(f"""
        This tool allows you to execute SQL queries on the connected database.
        The database has the following shape:
        <database>
        {ctx.deps.sql_dependency.get_prompt()}
        </database>
        IMPORTANT: {dialect_string}
    """)
    
    tool_def.description = tool_description
    
    return tool_def

    
    
@agent.tool(retries=5, prepare=prepare_sql_tool)
async def execute_sql_query(ctx: RunContext[State], query: str) -> PandasDataFrame:
    """Executes the SQL and returns the resulting table in JSON"""

    async def execute_query():
        with ThreadPoolExecutor() as executor:
            return await asyncio.get_event_loop().run_in_executor(
                executor,
                ctx.deps.sql_dependency.get_dataframe_from_query,
                query
            )

    try:
        result_df = await asyncio.wait_for(execute_query(), timeout=300)

                
        
    except asyncio.TimeoutError:
        raise ModelRetry("SQL query execution timed out after 300 seconds")
    
    except Exception as e:
        raise ModelRetry(f"Error while executing SQL query: {str(e)}")
    
    if result_df.empty:
        raise ModelRetry("The resulting DataFrame is empty. You may wanna check your filters.")
    
    result = SQLQueryResult(
        query=query,
        result=PandasDataFrame.model_validate(result_df.to_dict(orient="split"))
    )
    
    ctx.deps.sql_query_results.append(result)

    return result.result

async def prepare_plotly_tool(
    ctx: RunContext[State], tool_def: ToolDefinition
) -> ToolDefinition | None:
    
    if not len(ctx.deps.sql_query_results):
        return None
    
    tool_description = dedent(f"""
        This tool allows you to create visualizations using Plotly.
        
        You have access to a list of Pandas dataframe which are results of SQL queries you executed earlier.
        The list of dataframes are stores under the variable `dfs: List[pd.Dataframe]`. You can access each dataframe by its index, e.g. `dfs[0]` for the first dataframe.
        The dataframes have the following structure:
        <dataframes>
        {ctx.deps.get_sql_query_results_prompt()}
        </dataframes>
        
        DO NOT CREATE A NEW DATAFRAME OR OTHER DATA STRUCTURES.
        Use the existing Dataframes in `dfs` to create your visualizations.
        
        You have to assign the resulting figure to the variable `result`.
        DO NOT open the figure.
        
        Start with the following code snippet:
        
        ```python
        import plotly.express as px
        
        # Your code here
    """)
    
    tool_def.description = tool_description
    
    return tool_def
    

@agent.tool(retries=5, prepare=prepare_plotly_tool)
async def execute_plotly_code(ctx: RunContext[State], executable_python_code: str) -> PlotlyFigure:
    
    environment = get_plotly_environment(ctx=ctx)
    
    try:
        exec(executable_python_code, environment)
    except Exception as e:
        raise ModelRetry(f"Error while executing Plotly code: {str(e)}")

    if "result" in environment and isinstance(environment["result"], Figure):
                
        result_figure = environment["result"]
        result = PlotlyFigure.model_validate(json.loads(result_figure.to_json()))
        return result

    else:
        raise ModelRetry("No plotly figure was found under the variable `result`.")