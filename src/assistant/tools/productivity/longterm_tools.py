"""Tools for managing long-term goals."""
import uuid
import json
from datetime import datetime, date
from typing import Optional
from google.cloud import bigquery

PROJECT_ID = "gen-lang-client-0288149151"
TABLE_ID = f"{PROJECT_ID}.personal_assistant.long_term_goals"

VALID_STATUSES = ["active", "paused", "completed"]


def _get_client() -> bigquery.Client:
    return bigquery.Client(project=PROJECT_ID)


def create_goal(
    title: str,
    category: Optional[str] = None,
    description: Optional[str] = None,
    target_date: Optional[str] = None,
    milestones: Optional[list] = None,
) -> dict:
    """Create a new long-term goal.

    Args:
        title: Goal title (e.g. 'Run a marathon', 'Learn Spanish').
        category: Category (e.g. 'fitness', 'education', 'career', 'personal').
        description: Detailed description of the goal.
        target_date: Target completion date in YYYY-MM-DD format.
        milestones: List of milestone dicts with 'title' and 'target_date' keys.

    Returns:
        dict with 'status' and 'goal_id'.
    """
    goal_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    milestones_json = json.dumps(milestones or [])
    try:
        client = _get_client()
        rows = [{
            "goal_id": goal_id,
            "title": title,
            "category": category,
            "description": description,
            "target_date": target_date,
            "status": "active",
            "milestones": milestones_json,
            "created_at": now,
            "updated_at": now,
        }]
        errors = client.insert_rows_json(TABLE_ID, rows)
        if errors:
            return {"status": "error", "error_message": str(errors)}
        return {"status": "success", "goal_id": goal_id, "title": title}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def list_goals(status: Optional[str] = None) -> dict:
    """List long-term goals, optionally filtered by status.

    Args:
        status: active, paused, or completed (optional).

    Returns:
        dict with 'goals' list.
    """
    try:
        client = _get_client()
        conditions = ["1=1"]
        params = []
        if status and status in VALID_STATUSES:
            conditions.append("status = @status")
            params.append(bigquery.ScalarQueryParameter("status", "STRING", status))

        query = f"""
            SELECT goal_id, title, category, description, target_date, status, milestones
            FROM `{TABLE_ID}`
            WHERE {" AND ".join(conditions)}
            ORDER BY target_date ASC NULLS LAST
        """
        job_config = bigquery.QueryJobConfig(query_parameters=params)
        df = client.query(query, job_config=job_config).to_dataframe()
        goals = df.to_dict("records")
        for g in goals:
            if hasattr(g.get("target_date"), "isoformat"):
                g["target_date"] = g["target_date"].isoformat()
        return {"status": "success", "goals": goals, "count": len(goals)}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def update_goal_status(goal_id: str, status: str) -> dict:
    """Update the status of a long-term goal.

    Args:
        goal_id: The UUID of the goal.
        status: New status: active, paused, or completed.

    Returns:
        dict with 'status'.
    """
    if status not in VALID_STATUSES:
        return {"status": "error", "error_message": f"Invalid status. Use: {VALID_STATUSES}"}
    try:
        client = _get_client()
        now = datetime.utcnow().isoformat()
        params = [
            bigquery.ScalarQueryParameter("goal_id", "STRING", goal_id),
            bigquery.ScalarQueryParameter("status", "STRING", status),
            bigquery.ScalarQueryParameter("now", "STRING", now),
        ]
        query = f"""
            UPDATE `{TABLE_ID}`
            SET status = @status, updated_at = @now
            WHERE goal_id = @goal_id
        """
        client.query(query, job_config=bigquery.QueryJobConfig(query_parameters=params)).result()
        return {"status": "success", "goal_id": goal_id, "new_status": status}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}
