"""NewsAgent — manages news preferences and delivers briefings."""
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from agents.shared.calendar_agent import calendar_agent
from tools.social.news_tools import (
    add_news_topic,
    get_news_preferences,
    get_news_briefing,
)

news_agent = LlmAgent(
    name="NewsAgent",
    model="gemini-2.5-flash",
    description=(
        "Manages news topic preferences and generates news briefings. "
        "Use for setting up news interests, requesting a news summary, or scheduling news time."
    ),
    instruction="""
You are a personalized news curator.

When the user:
- Wants to add a news topic they care about → save it with add_news_topic
- Asks for news or a briefing → use get_news_briefing and generate a concise summary
- Wants to schedule a daily news reading time → use calendar_agent with event_type='news'

When generating a briefing, use your knowledge to provide a concise summary per topic.
Be clear that this uses your training knowledge and may not include very recent breaking news.

Format briefings cleanly with topic headers and 2-3 bullet points each.
""",
    tools=[
        add_news_topic,
        get_news_preferences,
        get_news_briefing,
        AgentTool(agent=calendar_agent),
    ],
    output_key="news_response",
)
