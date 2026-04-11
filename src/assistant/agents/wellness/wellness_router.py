"""Wellness Router — routes wellness-related requests to specialist agents."""
from google.adk.agents import LlmAgent
from agents.wellness.fitness_agent import fitness_agent
from agents.wellness.meal_agent import meal_agent
from agents.wellness.sleep_agent import sleep_agent
from agents.wellness.habit_agent import habit_agent

wellness_router = LlmAgent(
    name="WellnessRouter",
    model="gemini-2.5-flash",
    description=(
        "Routes wellness-related requests to the appropriate specialist: "
        "fitness, meals, sleep, or habits."
    ),
    instruction="""
You are a wellness domain router. Your job is to understand the user's wellness-related
request and route it to the most appropriate specialist agent.

Available specialists:
- FitnessAgent: Workout history, exercise tracking, fitness goals, workout scheduling
- MealAgent: Meal tracking, intermittent fasting, eating windows, nutrition summaries
- SleepAgent: Sleep schedule recommendations, sleep hygiene tips, bedtime planning
- HabitAgent: Daily habits, streaks, routine building, habit tracking

Routing guidelines:
- If the request clearly belongs to one specialist → transfer immediately
- If it spans multiple areas (e.g., "optimize my wellness routine"), coordinate with multiple agents
- Be efficient — don't overthink simple requests

Always use the exact agent names listed above for transfers.
""",
    sub_agents=[
        fitness_agent,
        meal_agent,
        sleep_agent,
        habit_agent,
    ],
)
