"""Tools for managing to-do tasks in BigQuery."""
import uuid
from datetime import datetime, timezone
from typing import Optional
from google.cloud import bigquery

PROJECT_ID = "gen-lang-client-0288149151"
TABLE_ID = f"{PROJECT_ID}.personal_assistant.tasks"


def _get_client() -> bigquery.Client:
    return bigquery.Client(project=PROJECT_ID)


def create_task(
    title: str,
    description: str = "",
    priority: str = "medium",
    category: str = "",
    due_date: str = "",
    parent_task_id: str = "",
) -> dict:
    """Create a new to-do task.

    Args:
        title: Short title for the task.
        description: Optional longer description.
        priority: 'low', 'medium', or 'high'.
        category: Optional category like 'school', 'fitness', 'finance'.
        due_date: Optional due date in YYYY-MM-DD format.
        parent_task_id: Optional parent task ID if this is a sub-step.

    Returns:
        dict with 'status' and created 'task'.
    """
    try:
        client = _get_client()
        task_id = str(uuid.uuid4())[:8]
        now = datetime.now(timezone.utc).isoformat()

        # Get next position for todo column
        pos_query = f"SELECT COALESCE(MAX(position), 0) + 1 as next_pos FROM `{TABLE_ID}` WHERE status = 'todo'"
        pos_result = list(client.query(pos_query).result())
        position = pos_result[0]["next_pos"] if pos_result else 1

        row = {
            "task_id": task_id,
            "parent_task_id": parent_task_id or None,
            "title": title,
            "description": description or None,
            "status": "todo",
            "priority": priority,
            "category": category or None,
            "due_date": due_date or None,
            "position": position,
            "created_at": now,
            "updated_at": now,
        }
        errors = client.insert_rows_json(TABLE_ID, [row])
        if errors:
            return {"status": "error", "error_message": str(errors)}
        return {"status": "success", "task": row}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def create_task_with_steps(
    title: str,
    steps: list[str],
    description: str = "",
    priority: str = "medium",
    category: str = "",
    due_date: str = "",
) -> dict:
    """Create a parent task and break it into sub-step tasks.

    Args:
        title: Title of the main task.
        steps: List of step titles to create as sub-tasks.
        description: Optional description for the parent task.
        priority: 'low', 'medium', or 'high'.
        category: Optional category.
        due_date: Optional due date in YYYY-MM-DD format.

    Returns:
        dict with 'status', parent 'task', and list of 'steps'.
    """
    try:
        client = _get_client()
        now = datetime.now(timezone.utc).isoformat()
        parent_id = str(uuid.uuid4())[:8]

        # Get next position
        pos_query = f"SELECT COALESCE(MAX(position), 0) as max_pos FROM `{TABLE_ID}` WHERE status = 'todo'"
        pos_result = list(client.query(pos_query).result())
        position = (pos_result[0]["max_pos"] if pos_result else 0) + 1

        parent_row = {
            "task_id": parent_id,
            "parent_task_id": None,
            "title": title,
            "description": description or None,
            "status": "todo",
            "priority": priority,
            "category": category or None,
            "due_date": due_date or None,
            "position": position,
            "created_at": now,
            "updated_at": now,
        }

        step_rows = []
        for i, step_title in enumerate(steps):
            step_rows.append({
                "task_id": str(uuid.uuid4())[:8],
                "parent_task_id": parent_id,
                "title": step_title,
                "description": None,
                "status": "todo",
                "priority": priority,
                "category": category or None,
                "due_date": None,
                "position": position + i + 1,
                "created_at": now,
                "updated_at": now,
            })

        all_rows = [parent_row] + step_rows
        errors = client.insert_rows_json(TABLE_ID, all_rows)
        if errors:
            return {"status": "error", "error_message": str(errors)}
        return {"status": "success", "task": parent_row, "steps": step_rows}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def update_task_status(task_id: str, status: str) -> dict:
    """Move a task to a different status column.

    Args:
        task_id: The task ID to update.
        status: New status: 'todo', 'in_progress', or 'done'.

    Returns:
        dict with 'status' and updated 'task_id'.
    """
    if status not in ("todo", "in_progress", "done"):
        return {"status": "error", "error_message": f"Invalid status: {status}. Use 'todo', 'in_progress', or 'done'."}
    try:
        client = _get_client()
        now = datetime.now(timezone.utc).isoformat()
        query = f"""
            UPDATE `{TABLE_ID}`
            SET status = @status, updated_at = @now
            WHERE task_id = @task_id
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("status", "STRING", status),
                bigquery.ScalarQueryParameter("now", "TIMESTAMP", now),
                bigquery.ScalarQueryParameter("task_id", "STRING", task_id),
            ]
        )
        client.query(query, job_config=job_config).result()
        return {"status": "success", "task_id": task_id, "new_status": status}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def update_task(
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    due_date: Optional[str] = None,
) -> dict:
    """Update task fields (title, description, priority, category, due_date).

    Args:
        task_id: The task ID to update.
        title: New title (optional).
        description: New description (optional).
        priority: New priority (optional).
        category: New category (optional).
        due_date: New due date in YYYY-MM-DD format (optional).

    Returns:
        dict with 'status' and updated field list.
    """
    sets = []
    params = [bigquery.ScalarQueryParameter("task_id", "STRING", task_id)]

    if title is not None:
        sets.append("title = @title")
        params.append(bigquery.ScalarQueryParameter("title", "STRING", title))
    if description is not None:
        sets.append("description = @description")
        params.append(bigquery.ScalarQueryParameter("description", "STRING", description))
    if priority is not None:
        sets.append("priority = @priority")
        params.append(bigquery.ScalarQueryParameter("priority", "STRING", priority))
    if category is not None:
        sets.append("category = @category")
        params.append(bigquery.ScalarQueryParameter("category", "STRING", category))
    if due_date is not None:
        sets.append("due_date = @due_date")
        params.append(bigquery.ScalarQueryParameter("due_date", "DATE", due_date))

    if not sets:
        return {"status": "error", "error_message": "No fields to update."}

    now = datetime.now(timezone.utc).isoformat()
    sets.append("updated_at = @now")
    params.append(bigquery.ScalarQueryParameter("now", "TIMESTAMP", now))

    try:
        client = _get_client()
        query = f"UPDATE `{TABLE_ID}` SET {', '.join(sets)} WHERE task_id = @task_id"
        job_config = bigquery.QueryJobConfig(query_parameters=params)
        client.query(query, job_config=job_config).result()
        return {"status": "success", "task_id": task_id, "updated_fields": [s.split(" = ")[0] for s in sets]}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def delete_task(task_id: str) -> dict:
    """Delete a task and all its sub-steps.

    Args:
        task_id: The task ID to delete.

    Returns:
        dict with 'status'.
    """
    try:
        client = _get_client()
        query = f"""
            DELETE FROM `{TABLE_ID}`
            WHERE task_id = @task_id OR parent_task_id = @task_id
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("task_id", "STRING", task_id),
            ]
        )
        client.query(query, job_config=job_config).result()
        return {"status": "success", "deleted_task_id": task_id}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def get_all_tasks() -> dict:
    """Get all tasks grouped by status for the kanban board.

    Returns:
        dict with 'status' and 'tasks' dict keyed by status column.
    """
    try:
        client = _get_client()
        query = f"""
            SELECT task_id, parent_task_id, title, description, status,
                   priority, category, due_date, position, created_at, updated_at
            FROM `{TABLE_ID}`
            ORDER BY position ASC, created_at ASC
        """
        df = client.query(query).to_dataframe()
        tasks = df.to_dict("records")
        for t in tasks:
            for field in ("created_at", "updated_at"):
                if hasattr(t.get(field), "isoformat"):
                    t[field] = t[field].isoformat()
            if hasattr(t.get("due_date"), "isoformat"):
                t["due_date"] = t["due_date"].isoformat()
            if t.get("due_date") is None:
                t["due_date"] = ""
            if t.get("parent_task_id") is None:
                t["parent_task_id"] = ""
        return {"status": "success", "tasks": tasks, "count": len(tasks)}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}
