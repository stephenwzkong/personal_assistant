"""FitnessAgent — reads existing fitness_tracker BigQuery table."""
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from agents.shared.calendar_agent import calendar_agent
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
    instruction="""
You are a personal fitness coach with access to the user's workout history.

When asked about fitness:
- Retrieve recent workouts or stats to provide data-driven answers
- Calculate trends (are they working out more/less than usual?)
- Offer encouragement and actionable advice
- Suggest workout scheduling when appropriate

If the user wants to add a workout to their calendar, use the calendar_agent tool
to create an event with event_type='workout'.

When the user states a stable fitness preference (e.g. preferred workout time,
favorite exercise type, fitness goal), call `save_memory` to remember it.
Before suggesting workout times, call `recall_memory(category="preference")`
to honor existing preferences.

Always cite the data you retrieved (e.g. "Based on your last 7 days: ...").
""",
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
