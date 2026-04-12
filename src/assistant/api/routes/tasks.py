"""Task endpoints — CRUD for the kanban board."""
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["tasks"])


class TaskOut(BaseModel):
    task_id: str
    parent_task_id: str = ""
    title: str
    description: str = ""
    status: str
    priority: str = "medium"
    category: str = ""
    due_date: str = ""
    position: int = 0
    created_at: str = ""
    updated_at: str = ""


class TasksResponse(BaseModel):
    tasks: list[TaskOut]
    count: int


class UpdateStatusRequest(BaseModel):
    status: str  # todo | in_progress | done


@router.get("/tasks")
async def list_tasks() -> TasksResponse:
    from tools.productivity.task_tools import get_all_tasks

    result = get_all_tasks()
    if result["status"] != "success":
        return TasksResponse(tasks=[], count=0)

    tasks = [
        TaskOut(
            task_id=t["task_id"],
            parent_task_id=t.get("parent_task_id") or "",
            title=t["title"],
            description=t.get("description") or "",
            status=t["status"],
            priority=t.get("priority") or "medium",
            category=t.get("category") or "",
            due_date=t.get("due_date") or "",
            position=t.get("position", 0),
            created_at=t.get("created_at") or "",
            updated_at=t.get("updated_at") or "",
        )
        for t in result["tasks"]
    ]
    return TasksResponse(tasks=tasks, count=len(tasks))


@router.patch("/tasks/{task_id}/status")
async def move_task(task_id: str, req: UpdateStatusRequest) -> dict:
    from tools.productivity.task_tools import update_task_status

    result = update_task_status(task_id, req.status)
    return result


@router.delete("/tasks/{task_id}")
async def remove_task(task_id: str) -> dict:
    from tools.productivity.task_tools import delete_task

    return delete_task(task_id)
