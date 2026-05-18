"""HabitAgent — tracks habits and logs completions."""
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from agents.shared.calendar_agent import calendar_agent
from skills.loader import load_skill_toolset
from tools.wellness.habit_tools import (
    create_habit,
    log_habit,
    get_habit_streak,
    list_habits,
)

habit_toolset = load_skill_toolset("habit", additional_tools=[
    create_habit,
    log_habit,
    get_habit_streak,
    list_habits,
    AgentTool(agent=calendar_agent),
])

habit_agent = LlmAgent(
    name="HabitAgent",
    model="gemini-2.5-flash",
    description=(
        "Tracks daily habits and streaks. Use for creating new habits, "
        "logging completions, and reviewing habit streaks."
    ),
    tools=[habit_toolset],
    output_key="habit_response",
)
