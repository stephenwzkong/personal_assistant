"""ReadingAgent — manages the user's reading list."""
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from agents.shared.calendar_agent import calendar_agent
from tools.productivity.reading_tools import (
    add_book,
    update_reading_progress,
    list_books,
)

reading_agent = LlmAgent(
    name="ReadingAgent",
    model="gemini-2.5-flash",
    description=(
        "Manages the user's reading list. Use for adding books, tracking reading progress, "
        "getting book recommendations, or scheduling reading time."
    ),
    instruction="""
You are a reading companion and book tracker.

When the user:
- Mentions a book they want to read → add it to the reading list
- Updates their reading progress → update current page and optionally status
- Asks what they're reading or want to read → list books by status
- Wants to schedule reading time → use calendar_agent with event_type='reading'

When a book is completed (current_page >= total_pages), mark status as 'completed'.
Celebrate completions! Ask if they'd like a brief discussion of the book.

You can also offer book recommendations based on what they've read and enjoyed.
""",
    tools=[
        add_book,
        update_reading_progress,
        list_books,
        AgentTool(agent=calendar_agent),
    ],
    output_key="reading_response",
)
