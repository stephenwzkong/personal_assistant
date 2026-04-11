"""HabitAgent — tracks habits and logs completions."""
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from agents.shared.calendar_agent import calendar_agent
from tools.wellness.habit_tools import (
    create_habit,
    log_habit,
    get_habit_streak,
    list_habits,
)

habit_agent = LlmAgent(
    name="HabitAgent",
    model="gemini-2.5-flash",
    description=(
        "Tracks daily habits and streaks. Use for creating new habits, "
        "logging completions, and reviewing habit streaks."
    ),
    instruction="""
You are a habit tracking coach that helps the user build consistent routines.

When the user:
- Wants to start a new habit → create it with create_habit
- Says they did their habit today → log it with log_habit
- Asks about their habits or streaks → list habits and show streak data
- Wants habit reminders on the calendar → use calendar_agent with event_type='task'

Be encouraging about streaks. If a streak is broken, be supportive and help them restart.
Show the streak count prominently — it's motivating!

For recurring habits, you can schedule them in bulk on the calendar if requested.
""",
    tools=[
        create_habit,
        log_habit,
        get_habit_streak,
        list_habits,
        AgentTool(agent=calendar_agent),
    ],
    output_key="habit_response",
)
