"""SleepAgent — provides sleep recommendations, cross-references fitness and school load."""
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from agents.shared.calendar_agent import calendar_agent
from agents.wellness.fitness_agent import fitness_agent
from tools.wellness.sleep_tools import (
    recommend_sleep_schedule,
    get_sleep_tips,
)

sleep_agent = LlmAgent(
    name="SleepAgent",
    model="gemini-2.5-flash",
    description=(
        "Provides personalized sleep recommendations and scheduling. "
        "Use for sleep advice, bedtime scheduling, or optimizing rest based on workout load."
    ),
    instruction="""
You are a sleep optimization coach.

When the user asks about sleep:
- Use recommend_sleep_schedule to calculate optimal bedtime based on their wake time and activities
- Check fitness_agent for recent workout intensity to adjust sleep recommendations
- Offer practical sleep hygiene tips for specific issues
- Schedule sleep windows on the calendar using calendar_agent with event_type='sleep'

Cross-agent awareness: If the user has had intense workouts recently (check fitness data),
recommend slightly longer sleep. If they mention a heavy school week, prioritize rest.

Always explain the reasoning behind your recommendations.
""",
    tools=[
        recommend_sleep_schedule,
        get_sleep_tips,
        AgentTool(agent=calendar_agent),
        AgentTool(agent=fitness_agent),
    ],
    output_key="sleep_response",
)
