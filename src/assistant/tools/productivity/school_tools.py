"""Tools for managing school assignments."""
import uuid
from datetime import datetime
from typing import Optional
from google.cloud import bigquery

PROJECT_ID = "gen-lang-client-0288149151"
TABLE_ID = f"{PROJECT_ID}.personal_assistant.school_assignments"

VALID_STATUSES = ["pending", "in_progress", "submitted", "graded"]
VALID_PRIORITIES = ["low", "medium", "high"]


def _get_client() -> bigquery.Client:
    return bigquery.Client(project=PROJECT_ID)


def create_assignment(
    course: str,
    title: str,
    due_date: Optional[str] = None,
    priority: str = "medium",
    description: Optional[str] = None,
) -> dict:
    """Create a new school assignment.

    Args:
        course: Course name (e.g. 'CS 101', 'Linear Algebra').
        title: Assignment title.
        due_date: Due date in ISO 8601 format (e.g. '2025-03-15T23:59:00').
        priority: low, medium, or high.
        description: Optional description.

    Returns:
        dict with 'status' and 'assignment_id' or 'error_message'.
    """
    if priority not in VALID_PRIORITIES:
        priority = "medium"
    assignment_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    try:
        client = _get_client()
        rows = [{
            "assignment_id": assignment_id,
            "course": course,
            "title": title,
            "due_date": due_date,
            "priority": priority,
            "status": "pending",
            "description": description,
            "grade": None,
            "created_at": now,
            "updated_at": now,
        }]
        errors = client.insert_rows_json(TABLE_ID, rows)
        if errors:
            return {"status": "error", "error_message": str(errors)}
        return {"status": "success", "assignment_id": assignment_id, "title": title, "course": course}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def list_assignments(
    status: Optional[str] = None,
    course: Optional[str] = None,
    limit: int = 20,
) -> dict:
    """List school assignments, optionally filtered.

    Args:
        status: Filter by status: pending, in_progress, submitted, graded (optional).
        course: Filter by course name (optional).
        limit: Max number of records (default 20).

    Returns:
        dict with 'status' and 'assignments' list.
    """
    try:
        client = _get_client()
        conditions = ["1=1"]
        params = []
        if status and status in VALID_STATUSES:
            conditions.append("status = @status")
            params.append(bigquery.ScalarQueryParameter("status", "STRING", status))
        if course:
            conditions.append("LOWER(course) LIKE LOWER(@course)")
            params.append(bigquery.ScalarQueryParameter("course", "STRING", f"%{course}%"))

        where_clause = " AND ".join(conditions)
        query = f"""
            SELECT assignment_id, course, title, due_date, priority, status, description, grade
            FROM `{TABLE_ID}`
            WHERE {where_clause}
            ORDER BY due_date ASC NULLS LAST
            LIMIT {limit}
        """
        job_config = bigquery.QueryJobConfig(query_parameters=params)
        df = client.query(query, job_config=job_config).to_dataframe()
        assignments = df.to_dict("records")
        for a in assignments:
            if hasattr(a.get("due_date"), "isoformat"):
                a["due_date"] = a["due_date"].isoformat()
        return {"status": "success", "assignments": assignments, "count": len(assignments)}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def update_assignment_status(assignment_id: str, status: str, grade: Optional[str] = None) -> dict:
    """Update the status of a school assignment.

    Args:
        assignment_id: The UUID of the assignment.
        status: New status: pending, in_progress, submitted, or graded.
        grade: Optional grade if status is 'graded'.

    Returns:
        dict with 'status' ('success' or 'error').
    """
    if status not in VALID_STATUSES:
        return {"status": "error", "error_message": f"Invalid status. Use: {VALID_STATUSES}"}
    try:
        client = _get_client()
        now = datetime.utcnow().isoformat()
        grade_set = ", grade = @grade" if grade else ""
        params = [
            bigquery.ScalarQueryParameter("assignment_id", "STRING", assignment_id),
            bigquery.ScalarQueryParameter("status", "STRING", status),
            bigquery.ScalarQueryParameter("now", "STRING", now),
        ]
        if grade:
            params.append(bigquery.ScalarQueryParameter("grade", "STRING", grade))

        query = f"""
            UPDATE `{TABLE_ID}`
            SET status = @status, updated_at = @now{grade_set}
            WHERE assignment_id = @assignment_id
        """
        job_config = bigquery.QueryJobConfig(query_parameters=params)
        client.query(query, job_config=job_config).result()
        return {"status": "success", "assignment_id": assignment_id}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}
