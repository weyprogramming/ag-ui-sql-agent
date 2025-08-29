import asyncio, json

from concurrent.futures import ThreadPoolExecutor

from pydantic_ai import Agent, RunContext, ModelRetry
from pydantic_ai.messages import ToolReturn
from pydantic_ai.ag_ui import StateDeps

from textwrap import dedent

from plotly.graph_objects import Figure

from state import State, SQLType
from result import PandasDataFrame, PlotlyFigure

from utils import get_plotly_environment



agent = Agent("openai:gpt-4o", deps_type=StateDeps[State])

@agent.instructions
def instructions(ctx: RunContext[State]) -> str:
    
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
        
    return f"""
        You are a SQL Expert working with the following SQL Database:
        <database>
        {ctx.deps.sql_dependency.get_prompt()}
        </database>
        Use the available tool to query the database based on the user's instruction.
        Explain the query you used to a non-technical user without mentioning technical details or the tool itself.
        Then, ask if the user is satisfied with the result or wants to make further adjustments.
        Respond in the user's language.
        IMPORTANT: {dialect_string}
    """
    
@agent.tool(retries=5)
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
    
    result = PandasDataFrame.model_validate(result_df.to_dict(orient="split"))
    
    ctx.deps.sql_query_result = result

    return result

@agent.tool(retries=5)
async def execute_plotly_code(ctx: RunContext[State], executable_python_code: str) -> PlotlyFigure:
    """
    Use this tool to visualize the data of the dataframe that was returned by the sql query.
    
    You can use the dataframe by using the variable `df`, which is already defined in the environment.
    
    You have to assign the resulting figure to the variable `result`.
    DO NOT open the figure.
    
    Start with the following code snippet:
    
    ```python
    import plotly.express as px
    import pandas as pd
    
    # Your code here
    ```
    """
    
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