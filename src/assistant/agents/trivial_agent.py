"""TrivialAgent — manages simple to-do tasks."""
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from agents.shared.calendar_agent import calendar_agent
from tools.trivial_tools import (
    create_task,
    list_tasks,
    complete_task,
)

trivial_agent = LlmAgent(
    name="TrivialAgent",
    model="gemini-2.5-flash",
    description=(
        "Manages simple tasks and to-do items. Use for quick errands, reminders, "
        "chores, and anything that needs to get done but isn't a major project."
    ),
    instruction="""
You are a task management assistant that helps the user track their to-do list.

When the user:
- Mentions something they need to do → create a task
- Asks what they need to do → list pending tasks, organized by priority
- Says they did something → mark it complete
- Wants to add a task to their calendar → use calendar_agent with event_type='task'

Keep things simple and actionable. Group similar tasks together when listing.
""",
    tools=[
        create_task,
        list_tasks,
        complete_task,
        AgentTool(agent=calendar_agent),
    ],
    output_key="trivial_response",
)
