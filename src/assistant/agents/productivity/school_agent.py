"""SchoolAgent — manages school assignments and schedules."""
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from agents.shared.calendar_agent import calendar_agent
from tools.productivity.school_tools import (
    create_assignment,
    list_assignments,
    update_assignment_status,
)

school_agent = LlmAgent(
    name="SchoolAgent",
    model="gemini-2.5-flash",
    description=(
        "Manages school assignments, tracks deadlines, and helps schedule study time. "
        "Use for anything related to courses, exams, homework, or academic planning."
    ),
    instruction="""
You are an academic assistant that helps the user stay on top of their coursework.

When the user mentions:
- An assignment, exam, or project → create it with create_assignment and add a calendar event
- Wanting to see what's due → list pending/in_progress assignments
- Completing something → update its status

When creating assignments, always also create a corresponding calendar event:
- Use calendar_agent with event_type='school'
- Set the calendar event to end at the due date/time
- Use priority matching the assignment priority

Be proactive: if the user has a heavy week, note it and suggest they prioritize.
""",
    tools=[
        create_assignment,
        list_assignments,
        update_assignment_status,
        AgentTool(agent=calendar_agent),
    ],
    output_key="school_response",
)
