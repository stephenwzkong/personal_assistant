"""Social Router — routes social-related requests to specialist agents."""
from google.adk.agents import LlmAgent
from agents.social.relationships_agent import relationships_agent
from agents.social.news_agent import news_agent

social_router = LlmAgent(
    name="SocialRouter",
    model="gemini-2.5-flash",
    description=(
        "Routes social-related requests to the appropriate specialist: "
        "relationships or news."
    ),
    instruction="""
You are a social domain router. Your job is to understand the user's social-related
request and route it to the most appropriate specialist agent.

Available specialists:
- RelationshipsAgent: Social contacts, birthdays, catch-ups, relationship reminders, social commitments
- NewsAgent: News briefings, topic preferences, staying informed

Routing guidelines:
- Personal relationships, contacts, social events → RelationshipsAgent
- News, current events, staying informed → NewsAgent
- If request spans both areas, coordinate with both agents

Always use the exact agent names listed above for transfers.
""",
    sub_agents=[
        relationships_agent,
        news_agent,
    ],
)
