from cryptography.fernet import Fernet
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response

from aredis_om import get_redis_connection

from pydantic_ai.ag_ui import handle_ag_ui_request, StateDeps

import logfire

from dotenv import load_dotenv
load_dotenv()

from states.dashboard_state import DashboardState
from models.dashboard_config_models import DashboardConfigModel
from models.sql_dependency_model import SQLBaseDependencyModel
from settings import settings
from agents.dashboard_agent import dashboard_agent
from api.dashboard_config import router as dashboard_router
from api.agent_state import agent_state_router
from api.dashboard_evaluation import dashboard_evaluation_router
from api.sql_dependency import sql_dependency_router

redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLBaseDependencyModel.Meta.database = get_redis_connection(
        url=redis_url,
        decode_responses=True
    )
    
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard_router, prefix="/api")
app.include_router(agent_state_router, prefix="/api")
app.include_router(dashboard_evaluation_router, prefix="/api")
app.include_router(sql_dependency_router, prefix="/api")

@app.post("/")
async def run_agent(request: Request) -> Response:
    
    return await handle_ag_ui_request(
        agent=dashboard_agent, 
        request=request,
        deps=StateDeps(DashboardState())
    )
    
logfire.configure()
logfire.instrument_fastapi(app)
logfire.instrument_pydantic_ai(dashboard_agent)