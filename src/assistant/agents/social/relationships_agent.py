"""RelationshipsAgent — manages social contacts and relationship reminders."""
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from agents.shared.calendar_agent import calendar_agent
from prompts.loader import build_instruction
from tools.social.relationships_tools import (
    add_contact,
    log_contact,
    get_contacts_to_reach_out,
    list_contacts,
)

relationships_agent = LlmAgent(
    name="RelationshipsAgent",
    model="gemini-2.5-flash",
    description=(
        "Manages social relationships and contact reminders. "
        "Use for tracking friends/family, logging catch-ups, and setting reminder to reach out."
    ),
    instruction=build_instruction("social/relationships.md", "social/relationships.md"),
    tools=[
        add_contact,
        log_contact,
        get_contacts_to_reach_out,
        list_contacts,
        AgentTool(agent=calendar_agent),
    ],
    output_key="relationships_response",
)
