"""TrivialAgent — manages simple to-do tasks."""
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from agents.shared.calendar_agent import calendar_agent
from skills.loader import load_skill_toolset
from tools.trivial_tools import (
    create_task,
    list_tasks,
    complete_task,
)

trivial_toolset = load_skill_toolset("trivial", additional_tools=[
    create_task,
    list_tasks,
    complete_task,
    AgentTool(agent=calendar_agent),
])

trivial_agent = LlmAgent(
    name="TrivialAgent",
    model="gemini-2.5-flash",
    description=(
        "Manages simple tasks and to-do items. Use for quick errands, reminders, "
        "chores, and anything that needs to get done but isn't a major project."
    ),
    tools=[trivial_toolset],
    output_key="trivial_response",
)
