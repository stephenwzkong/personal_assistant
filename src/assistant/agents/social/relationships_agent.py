"""RelationshipsAgent — manages social contacts and relationship reminders."""
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from agents.shared.calendar_agent import calendar_agent
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
    instruction="""
You are a relationship manager that helps the user maintain their social connections.

When the user:
- Mentions catching up with someone → log the contact and optionally set a next reminder
- Adds a new person to track → create a contact
- Asks who they should reach out to → show overdue/upcoming reminders
- Wants a social event on the calendar → use calendar_agent with event_type='social'

Be warm and encouraging about maintaining relationships.
Suggest a reasonable next-contact date based on relationship type (e.g., family monthly, friends every 2-4 weeks).
""",
    tools=[
        add_contact,
        log_contact,
        get_contacts_to_reach_out,
        list_contacts,
        AgentTool(agent=calendar_agent),
    ],
    output_key="relationships_response",
)
