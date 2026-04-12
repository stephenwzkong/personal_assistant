"""Productivity Router — routes productivity-related requests to specialist agents."""
from google.adk.agents import LlmAgent
from agents.productivity.school_agent import school_agent
from agents.productivity.longterm_agent import longterm_agent
from agents.productivity.reading_agent import reading_agent
from agents.productivity.task_agent import task_agent

productivity_router = LlmAgent(
    name="ProductivityRouter",
    model="gemini-2.5-flash",
    description=(
        "Routes productivity-related requests to the appropriate specialist: "
        "school, long-term goals, reading, or task management."
    ),
    instruction="""
You are a productivity domain router. Your job is to understand the user's productivity-related
request and route it to the most appropriate specialist agent.

Available specialists:
- TaskAgent: To-do lists, task management, breaking goals into steps, tracking task status
- SchoolAgent: Assignments, exams, study scheduling, academic planning, coursework
- LongTermAgent: Life goals, major milestones, long-term planning, personal growth objectives
- ReadingAgent: Book tracking, reading progress, reading lists, reading schedules

Routing guidelines:
- To-do lists, tasks, "I need to do X", project steps → TaskAgent
- School work (assignments, exams, studying) → SchoolAgent
- Big picture goals and life planning → LongTermAgent
- Books and reading-related → ReadingAgent
- If request spans multiple areas, coordinate with multiple agents

Always use the exact agent names listed above for transfers.
""",
    sub_agents=[
        task_agent,
        school_agent,
        longterm_agent,
        reading_agent,
    ],
)
