"""CalendarAgent — owns all calendar CRUD tools."""
from google.adk.agents import LlmAgent
from tools.shared.calendar_tools import (
    create_calendar_event,
    list_calendar_events,
    get_events_in_range,
    update_calendar_event,
    delete_calendar_event,
)

calendar_agent = LlmAgent(
    name="CalendarAgent",
    model="gemini-2.5-flash",
    description=(
        "Manages the user's calendar. Can create, list, update, and delete events. "
        "Call this agent to schedule anything, check availability, or modify existing events."
    ),
    instruction="""
You are a calendar management assistant. You help the user manage their personal calendar
stored in BigQuery.

When creating events, always confirm:
- Title: clear, descriptive name
- Start/end datetime in ISO 8601 format (e.g. 2025-03-10T09:00:00)
- Event type from: workout, meal_window, school, sleep, task, finance, social, reading, news, goal, other

When listing events, present them in a clean, readable format with dates and times.
If the user says "today", use today's date. If they say "this week", use the current week's
Monday to Sunday range.

Always confirm successful operations with a brief summary.
""",
    tools=[
        create_calendar_event,
        list_calendar_events,
        get_events_in_range,
        update_calendar_event,
        delete_calendar_event,
    ],
    output_key="calendar_response",
)
