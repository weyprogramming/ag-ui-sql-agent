from cryptography.fernet import Fernet
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response

from aredis_om import get_redis_connection

from pydantic_ai.ag_ui import handle_ag_ui_request, StateDeps


from dotenv import load_dotenv
load_dotenv()

from deps.current_sql_dep import current_sql_dep
from states.dashboard_state import State, DashboardState
from models.dashboard_config_models import DashboardConfigModel
from settings import settings
from agents.dashboard_agent import dashboard_agent
from api.dashboard_config import router as dashboard_router
from api.agent_state import agent_state_router
from api.dashboard_evaluation import dashboard_evaluation_router

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
app.include_router(dashboard_evaluation_router, prefix="/api")

@app.post("/")
async def run_agent(request: Request) -> Response:
    
    deps = State(sql_dependency=current_sql_dep, state=DashboardState())
    
    return await handle_ag_ui_request(
        agent=dashboard_agent, 
        request=request,
        deps=deps
    )