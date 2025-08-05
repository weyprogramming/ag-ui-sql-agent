from pydantic_ai import Agent
from pydantic_ai.ag_ui import StateDeps

from state import State

agent = Agent("openai:gpt-4o", deps_type=StateDeps[State])