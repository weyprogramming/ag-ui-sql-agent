from cryptography.fernet import Fernet

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response

from pydantic_ai import Agent
from pydantic_ai.ag_ui import handle_ag_ui_request, StateDeps


from dotenv import load_dotenv
load_dotenv()

from state import State, SQLBaseDependency, SQLConnectionParams, SQLType
from settings import settings
from agent import agent



sql_connection_params = SQLConnectionParams(
    type=SQLType.MSSQL,
    host="localhost",
    port=1433,
    database="German",
    username="sa",
    encrypted_password=Fernet(settings.DB_PASSWORD_KEY.encode()).encrypt("Administrator0803".encode())
)

sql_dep = SQLBaseDependency(
    name="Tradedatabase",
    connection_params=sql_connection_params,
)

metadata = sql_dep.get_metadata()
sql_dep.set_tables_from_metadata(metadata)

state_deps = StateDeps(State(sql_dependencies=[sql_dep]))

app = FastAPI()


@app.post("/")
async def run_agent(request: Request) -> Response:
    return await handle_ag_ui_request(
        agent=agent, 
        request=request,
        deps=StateDeps(State())
    )