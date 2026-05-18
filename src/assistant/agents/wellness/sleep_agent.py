"""SleepAgent — provides sleep recommendations, cross-references fitness and school load."""
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from agents.shared.calendar_agent import calendar_agent
from agents.wellness.fitness_agent import fitness_agent
from skills.loader import load_skill_toolset
from tools.wellness.sleep_tools import (
    recommend_sleep_schedule,
    get_sleep_tips,
)

sleep_toolset = load_skill_toolset("sleep", additional_tools=[
    recommend_sleep_schedule,
    get_sleep_tips,
    AgentTool(agent=calendar_agent),
    AgentTool(agent=fitness_agent),
])

sleep_agent = LlmAgent(
    name="SleepAgent",
    model="gemini-2.5-flash",
    description=(
        "Provides personalized sleep recommendations and scheduling. "
        "Use for sleep advice, bedtime scheduling, or optimizing rest based on workout load."
    ),
    tools=[sleep_toolset],
    output_key="sleep_response",
)
