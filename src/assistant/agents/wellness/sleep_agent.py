"""SleepAgent — provides sleep recommendations, cross-references fitness and school load."""
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from agents.shared.calendar_agent import calendar_agent
from agents.wellness.fitness_agent import fitness_agent
from prompts.loader import build_instruction
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
    instruction=build_instruction("wellness/sleep.md", "wellness/sleep.md"),
    tools=[
        recommend_sleep_schedule,
        get_sleep_tips,
        AgentTool(agent=calendar_agent),
        AgentTool(agent=fitness_agent),
    ],
    output_key="sleep_response",
)
