from fastapi import APIRouter

from states.dashboard_state import DashboardState


agent_state_router = APIRouter()

@agent_state_router.get("/state/{state_id}")
async def get_agent_state(state_id: str) -> DashboardState:
    return {"state_id": state_id, "status": "active"}

