"""TaskAgent — manages to-do tasks with kanban-style workflow."""
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from agents.shared.calendar_agent import calendar_agent
from skills.loader import load_skill_toolset
from tools.productivity.task_tools import (
    create_task,
    create_task_with_steps,
    update_task_status,
    update_task,
    delete_task,
    get_all_tasks,
)
from tools.shared.memory_tools import save_memory, recall_memory

task_toolset = load_skill_toolset("task", additional_tools=[
    create_task,
    create_task_with_steps,
    update_task_status,
    update_task,
    delete_task,
    get_all_tasks,
    AgentTool(agent=calendar_agent),
    save_memory,
    recall_memory,
])

task_agent = LlmAgent(
    name="TaskAgent",
    model="gemini-2.5-flash",
    description=(
        "Manages to-do lists and tasks. Can create tasks, break goals into steps, "
        "move tasks between statuses (todo, in_progress, done), and track progress. "
        "Use this for any to-do, task management, or project planning request."
    ),
    tools=[task_toolset],
    output_key="task_response",
)
