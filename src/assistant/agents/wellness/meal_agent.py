"""MealAgent — reads existing meal_hour BigQuery table."""
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from agents.shared.calendar_agent import calendar_agent
from prompts.loader import build_instruction
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
    instruction=build_instruction("wellness/meal.md", "wellness/meal.md"),
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
