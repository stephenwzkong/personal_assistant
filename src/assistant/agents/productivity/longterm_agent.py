"""LongTermAgent — tracks long-term goals and milestones."""
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from agents.shared.calendar_agent import calendar_agent
from tools.productivity.longterm_tools import (
    create_goal,
    list_goals,
    update_goal_status,
)
from tools.shared.memory_tools import save_memory, recall_memory

longterm_agent = LlmAgent(
    name="LongTermAgent",
    model="gemini-2.5-flash",
    description=(
        "Manages long-term goals and life objectives. Use for setting big goals, "
        "tracking progress toward major life milestones, or reviewing your roadmap."
    ),
    instruction="""
You are a life coach focused on long-term goal achievement.

When the user:
- Mentions a big goal or ambition → create it with milestones if applicable
- Asks about their goals → list active goals and their progress
- Achieves a goal or milestone → update its status
- Wants milestone reminders → schedule them using calendar_agent with event_type='goal'

Be strategic and thoughtful. Help break big goals into concrete milestones.
Connect goals to other areas: fitness goals → fitness agent data, reading goals → reading agent, etc.

When the user reveals deep motivations, life values, or long-term aspirations,
call `save_memory(category="goal", ...)` so future sessions can reference them.
Use `recall_memory(category="goal")` when reviewing progress or planning.

Always acknowledge progress and provide motivational context for why goals matter.
""",
    tools=[
        create_goal,
        list_goals,
        update_goal_status,
        AgentTool(agent=calendar_agent),
        save_memory,
        recall_memory,
    ],
    output_key="longterm_response",
)
