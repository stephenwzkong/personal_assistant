"""MealAgent — reads existing meal_hour BigQuery table."""
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from agents.shared.calendar_agent import calendar_agent
from tools.wellness.meal_tools import (
    get_recent_meals,
    get_meal_summary,
    get_eating_window_today,
)
from tools.shared.memory_tools import save_memory, recall_memory

meal_agent = LlmAgent(
    name="MealAgent",
    model="gemini-2.5-flash",
    description=(
        "Provides meal tracking insights, intermittent fasting window data, "
        "and nutrition summaries from the user's meal log."
    ),
    instruction="""
You are a nutrition and intermittent fasting assistant with access to the user's meal history.

When asked about nutrition or eating:
- Retrieve meal data to give accurate summaries
- Report on the user's eating window (intermittent fasting compliance)
- Provide trends and patterns in eating habits
- Offer helpful nutritional advice based on their logs

If the user wants to schedule meal windows or fasting periods on their calendar,
use the calendar_agent tool with event_type='meal_window'.

When the user states a dietary preference or constraint (vegetarian, allergies,
fasting window, etc.), call `save_memory` to remember it. Before recommending
foods or windows, call `recall_memory(query="diet")` to honor constraints.

Always be encouraging and supportive about dietary goals.
""",
    tools=[
        get_recent_meals,
        get_meal_summary,
        get_eating_window_today,
        AgentTool(agent=calendar_agent),
        save_memory,
        recall_memory,
    ],
    output_key="meal_response",
)
