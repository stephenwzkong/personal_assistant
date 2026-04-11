"""Calendar CRUD tools for BigQuery-backed calendar events."""
import uuid
from datetime import datetime
from typing import Optional
from google.cloud import bigquery

PROJECT_ID = "gen-lang-client-0288149151"
DATASET = "personal_assistant"
TABLE = "calendar_events"
TABLE_ID = f"{PROJECT_ID}.{DATASET}.{TABLE}"

EVENT_COLORS = {
    "workout": "#10B981",
    "meal_window": "#F59E0B",
    "school": "#3B82F6",
    "sleep": "#8B5CF6",
    "task": "#6B7280",
    "finance": "#EF4444",
    "social": "#EC4899",
    "reading": "#0EA5E9",
    "news": "#14B8A6",
    "goal": "#F97316",
    "other": "#94A3B8",
}

VALID_EVENT_TYPES = list(EVENT_COLORS.keys())
VALID_STATUSES = ["active", "cancelled", "completed"]
VALID_PRIORITIES = ["low", "medium", "high"]


def _get_client() -> bigquery.Client:
    return bigquery.Client(project=PROJECT_ID)


def create_calendar_event(
    title: str,
    start_datetime: str,
    end_datetime: str,
    event_type: str = "other",
    source_agent: Optional[str] = None,
    priority: Optional[str] = "medium",
    description: Optional[str] = None,
) -> dict:
    """Create a new calendar event.

    Args:
        title: Event title.
        start_datetime: Start datetime in ISO 8601 format (e.g. '2025-03-10T09:00:00').
        end_datetime: End datetime in ISO 8601 format (e.g. '2025-03-10T10:00:00').
        event_type: One of: workout, meal_window, school, sleep, task, finance, social,
                    reading, news, goal, other.
        source_agent: Name of the agent creating the event.
        priority: low, medium, or high.
        description: Optional description.

    Returns:
        dict with 'status' ('success' or 'error') and 'event_id' or 'error_message'.
    """
    if event_type not in VALID_EVENT_TYPES:
        event_type = "other"
    if priority not in VALID_PRIORITIES:
        priority = "medium"

    event_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    try:
        client = _get_client()
        rows = [{
            "event_id": event_id,
            "title": title,
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "event_type": event_type,
            "source_agent": source_agent,
            "priority": priority,
            "status": "active",
            "description": description,
            "metadata": None,
            "created_at": now,
            "updated_at": now,
        }]
        errors = client.insert_rows_json(TABLE_ID, rows)
        if errors:
            return {"status": "error", "error_message": str(errors)}
        return {"status": "success", "event_id": event_id, "title": title}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def list_calendar_events(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 20,
) -> dict:
    """List calendar events, optionally filtered by date range or type.

    Args:
        start_date: Filter events starting from this date (YYYY-MM-DD).
        end_date: Filter events up to this date (YYYY-MM-DD).
        event_type: Filter by event type (optional).
        limit: Maximum number of events to return (default 20).

    Returns:
        dict with 'status' and 'events' list or 'error_message'.
    """
    try:
        client = _get_client()
        conditions = ["status = 'active'"]
        if start_date:
            conditions.append(f"DATE(start_datetime) >= '{start_date}'")
        if end_date:
            conditions.append(f"DATE(start_datetime) <= '{end_date}'")
        if event_type and event_type in VALID_EVENT_TYPES:
            conditions.append(f"event_type = '{event_type}'")

        where_clause = " AND ".join(conditions)
        query = f"""
            SELECT event_id, title, start_datetime, end_datetime, event_type,
                   source_agent, priority, status, description
            FROM `{TABLE_ID}`
            WHERE {where_clause}
            ORDER BY start_datetime ASC
            LIMIT {limit}
        """
        df = client.query(query).to_dataframe()
        events = df.to_dict("records")
        # Convert timestamps to strings for serialization
        for e in events:
            for k in ("start_datetime", "end_datetime"):
                if hasattr(e[k], "isoformat"):
                    e[k] = e[k].isoformat()
        return {"status": "success", "events": events, "count": len(events)}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def get_events_in_range(start_date: str, end_date: str) -> dict:
    """Get all active events between two dates (inclusive).

    Args:
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.

    Returns:
        dict with 'status' and 'events' list or 'error_message'.
    """
    return list_calendar_events(start_date=start_date, end_date=end_date, limit=200)


def update_calendar_event(
    event_id: str,
    title: Optional[str] = None,
    start_datetime: Optional[str] = None,
    end_datetime: Optional[str] = None,
    status: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
) -> dict:
    """Update an existing calendar event by ID.

    Args:
        event_id: The UUID of the event to update.
        title: New title (optional).
        start_datetime: New start datetime in ISO 8601 format (optional).
        end_datetime: New end datetime in ISO 8601 format (optional).
        status: New status: active, cancelled, or completed (optional).
        description: New description (optional).
        priority: New priority: low, medium, or high (optional).

    Returns:
        dict with 'status' ('success' or 'error').
    """
    if status and status not in VALID_STATUSES:
        return {"status": "error", "error_message": f"Invalid status. Use: {VALID_STATUSES}"}

    updates = {"updated_at": datetime.utcnow().isoformat()}
    if title is not None:
        updates["title"] = title
    if start_datetime is not None:
        updates["start_datetime"] = start_datetime
    if end_datetime is not None:
        updates["end_datetime"] = end_datetime
    if status is not None:
        updates["status"] = status
    if description is not None:
        updates["description"] = description
    if priority is not None:
        updates["priority"] = priority

    set_clauses = ", ".join([f"{k} = @{k}" for k in updates])
    params = [
        bigquery.ScalarQueryParameter(k, "STRING", v)
        for k, v in updates.items()
    ]
    params.append(bigquery.ScalarQueryParameter("event_id", "STRING", event_id))

    query = f"UPDATE `{TABLE_ID}` SET {set_clauses} WHERE event_id = @event_id"

    try:
        client = _get_client()
        job_config = bigquery.QueryJobConfig(query_parameters=params)
        client.query(query, job_config=job_config).result()
        return {"status": "success", "event_id": event_id}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def delete_calendar_event(event_id: str) -> dict:
    """Cancel (soft-delete) a calendar event by setting status to 'cancelled'.

    Args:
        event_id: The UUID of the event to cancel.

    Returns:
        dict with 'status' ('success' or 'error').
    """
    return update_calendar_event(event_id=event_id, status="cancelled")
