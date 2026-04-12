"""FitnessAgent — reads existing fitness_tracker BigQuery table."""
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from agents.shared.calendar_agent import calendar_agent
from prompts.loader import build_instruction
from tools.wellness.fitness_tools import (
    get_recent_workouts,
    get_workout_stats,
    get_workouts_by_type,
)
from tools.shared.memory_tools import save_memory, recall_memory

fitness_agent = LlmAgent(
    name="FitnessAgent",
    model="gemini-2.5-flash",
    description=(
        "Provides fitness insights, workout history, and stats from the user's workout log. "
        "Can also schedule workouts on the calendar."
    ),
    instruction=build_instruction("wellness/fitness.md", "wellness/fitness.md"),
    tools=[
        get_recent_workouts,
        get_workout_stats,
        get_workouts_by_type,
        AgentTool(agent=calendar_agent),
        save_memory,
        recall_memory,
    ],
    output_key="fitness_response",
)
