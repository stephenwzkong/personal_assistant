"""SchoolAgent — manages school assignments and schedules."""
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from agents.shared.calendar_agent import calendar_agent
from prompts.loader import build_instruction
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
    instruction=build_instruction("productivity/school.md", "productivity/school.md"),
    tools=[
        create_assignment,
        list_assignments,
        update_assignment_status,
        AgentTool(agent=calendar_agent),
    ],
    output_key="school_response",
)
