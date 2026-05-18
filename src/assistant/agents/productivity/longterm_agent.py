"""LongTermAgent — tracks long-term goals and milestones."""
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from agents.shared.calendar_agent import calendar_agent
from skills.loader import load_skill_toolset
from tools.productivity.longterm_tools import (
    create_goal,
    list_goals,
    update_goal_status,
)
from tools.shared.memory_tools import save_memory, recall_memory

longterm_toolset = load_skill_toolset("longterm", additional_tools=[
    create_goal,
    list_goals,
    update_goal_status,
    AgentTool(agent=calendar_agent),
    save_memory,
    recall_memory,
])

longterm_agent = LlmAgent(
    name="LongTermAgent",
    model="gemini-2.5-flash",
    description=(
        "Manages long-term goals and life objectives. Use for setting big goals, "
        "tracking progress toward major life milestones, or reviewing your roadmap."
    ),
    tools=[longterm_toolset],
    output_key="longterm_response",
)
