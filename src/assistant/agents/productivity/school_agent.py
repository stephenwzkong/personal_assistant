"""SchoolAgent — manages school assignments and schedules."""
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from agents.shared.calendar_agent import calendar_agent
from skills.loader import load_skill_toolset
from tools.productivity.school_tools import (
    create_assignment,
    list_assignments,
    update_assignment_status,
)

school_toolset = load_skill_toolset("school", additional_tools=[
    create_assignment,
    list_assignments,
    update_assignment_status,
    AgentTool(agent=calendar_agent),
])

school_agent = LlmAgent(
    name="SchoolAgent",
    model="gemini-2.5-flash",
    description=(
        "Manages school assignments, tracks deadlines, and helps schedule study time. "
        "Use for anything related to courses, exams, homework, or academic planning."
    ),
    tools=[school_toolset],
    output_key="school_response",
)
