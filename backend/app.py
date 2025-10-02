from cryptography.fernet import Fernet
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response

from aredis_om import get_redis_connection

from pydantic_ai.ag_ui import handle_ag_ui_request, StateDeps


from dotenv import load_dotenv
load_dotenv()

from deps.sql_dependency import SQLBaseDependency, SQLConnectionParams, SQLType
from states.dashboard_state import DashboardState
from models.dashboard_config_models import DashboardConfigModel
from settings import settings
from agents.dashboard_agent import dashboard_agent
from api.dashboard import router as dashboard_router
from api.agent_state import agent_state_router

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

redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"

@asynccontextmanager
async def lifespan(app: FastAPI):
    DashboardConfigModel.Meta.database = get_redis_connection(
        url=redis_url,
        decode_responses=True
    )
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(dashboard_router, prefix="/api")
app.include_router(agent_state_router, prefix="/api")

@app.post("/")
async def run_agent(request: Request) -> Response:
    
    deps = DashboardState(sql_dependency=sql_dep)
    
    return await handle_ag_ui_request(
        agent=dashboard_agent, 
        request=request,
        deps=deps
    )