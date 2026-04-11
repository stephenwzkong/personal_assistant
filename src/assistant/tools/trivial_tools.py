"""Tools for managing trivial tasks."""
import uuid
from datetime import datetime
from typing import Optional
from google.cloud import bigquery

PROJECT_ID = "gen-lang-client-0288149151"
TABLE_ID = f"{PROJECT_ID}.personal_assistant.trivial_tasks"

VALID_STATUSES = ["pending", "done", "deferred"]
VALID_PRIORITIES = ["low", "medium", "high"]


def _get_client() -> bigquery.Client:
    return bigquery.Client(project=PROJECT_ID)


def create_task(
    title: str,
    category: Optional[str] = None,
    due_date: Optional[str] = None,
    priority: str = "medium",
    notes: Optional[str] = None,
) -> dict:
    """Create a new trivial task.

    Args:
        title: Task title.
        category: Optional category (e.g. 'errands', 'home', 'work').
        due_date: Optional due date in ISO 8601 format.
        priority: low, medium, or high.
        notes: Optional notes.

    Returns:
        dict with 'status' and 'task_id' or 'error_message'.
    """
    if priority not in VALID_PRIORITIES:
        priority = "medium"
    task_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    try:
        client = _get_client()
        rows = [{
            "task_id": task_id,
            "title": title,
            "category": category,
            "due_date": due_date,
            "priority": priority,
            "status": "pending",
            "notes": notes,
            "created_at": now,
            "updated_at": now,
        }]
        errors = client.insert_rows_json(TABLE_ID, rows)
        if errors:
            return {"status": "error", "error_message": str(errors)}
        return {"status": "success", "task_id": task_id, "title": title}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def list_tasks(status: Optional[str] = None, limit: int = 20) -> dict:
    """List tasks, optionally filtered by status.

    Args:
        status: pending, done, or deferred (optional, lists all if omitted).
        limit: Max number of results.

    Returns:
        dict with 'status' and 'tasks' list.
    """
    try:
        client = _get_client()
        conditions = ["1=1"]
        params = []
        if status and status in VALID_STATUSES:
            conditions.append("status = @status")
            params.append(bigquery.ScalarQueryParameter("status", "STRING", status))

        query = f"""
            SELECT task_id, title, category, due_date, priority, status, notes
            FROM `{TABLE_ID}`
            WHERE {" AND ".join(conditions)}
            ORDER BY
                CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END,
                due_date ASC NULLS LAST
            LIMIT {limit}
        """
        job_config = bigquery.QueryJobConfig(query_parameters=params)
        df = client.query(query, job_config=job_config).to_dataframe()
        tasks = df.to_dict("records")
        for t in tasks:
            if hasattr(t.get("due_date"), "isoformat"):
                t["due_date"] = t["due_date"].isoformat()
        return {"status": "success", "tasks": tasks, "count": len(tasks)}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def complete_task(task_id: str) -> dict:
    """Mark a task as done.

    Args:
        task_id: The UUID of the task.

    Returns:
        dict with 'status' ('success' or 'error').
    """
    try:
        client = _get_client()
        now = datetime.utcnow().isoformat()
        params = [
            bigquery.ScalarQueryParameter("task_id", "STRING", task_id),
            bigquery.ScalarQueryParameter("now", "STRING", now),
        ]
        query = f"UPDATE `{TABLE_ID}` SET status = 'done', updated_at = @now WHERE task_id = @task_id"
        client.query(query, job_config=bigquery.QueryJobConfig(query_parameters=params)).result()
        return {"status": "success", "task_id": task_id}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}
