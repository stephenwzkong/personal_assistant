"""NewsAgent — manages news preferences and delivers briefings."""
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from agents.shared.calendar_agent import calendar_agent
from skills.loader import load_skill_toolset
from tools.social.news_tools import (
    add_news_topic,
    get_news_preferences,
    get_news_briefing,
)

news_toolset = load_skill_toolset("news", additional_tools=[
    add_news_topic,
    get_news_preferences,
    get_news_briefing,
    AgentTool(agent=calendar_agent),
])

news_agent = LlmAgent(
    name="NewsAgent",
    model="gemini-2.5-flash",
    description=(
        "Manages news topic preferences and generates news briefings. "
        "Use for setting up news interests, requesting a news summary, or scheduling news time."
    ),
    tools=[news_toolset],
    output_key="news_response",
)
