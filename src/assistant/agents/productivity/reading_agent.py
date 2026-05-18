"""ReadingAgent — manages the user's reading list."""
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from agents.shared.calendar_agent import calendar_agent
from skills.loader import load_skill_toolset
from tools.productivity.reading_tools import (
    add_book,
    update_reading_progress,
    list_books,
)

reading_toolset = load_skill_toolset("reading", additional_tools=[
    add_book,
    update_reading_progress,
    list_books,
    AgentTool(agent=calendar_agent),
])

reading_agent = LlmAgent(
    name="ReadingAgent",
    model="gemini-2.5-flash",
    description=(
        "Manages the user's reading list. Use for adding books, tracking reading progress, "
        "getting book recommendations, or scheduling reading time."
    ),
    tools=[reading_toolset],
    output_key="reading_response",
)
