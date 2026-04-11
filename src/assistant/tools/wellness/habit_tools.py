"""Tools for managing habits and habit logs."""
import uuid
from datetime import datetime, date
from typing import Optional
from google.cloud import bigquery

PROJECT_ID = "gen-lang-client-0288149151"
HABITS_TABLE = f"{PROJECT_ID}.personal_assistant.habits"
LOGS_TABLE = f"{PROJECT_ID}.personal_assistant.habit_logs"

VALID_FREQUENCIES = ["daily", "weekdays", "weekly"]


def _get_client() -> bigquery.Client:
    return bigquery.Client(project=PROJECT_ID)


def create_habit(
    name: str,
    frequency: str = "daily",
    target_count: int = 1,
    description: Optional[str] = None,
) -> dict:
    """Create a new habit to track.

    Args:
        name: Habit name (e.g. 'Morning run', 'Read 30 minutes').
        frequency: daily, weekdays, or weekly.
        target_count: Target completions per period (default 1).
        description: Optional description.

    Returns:
        dict with 'status' and 'habit_id'.
    """
    if frequency not in VALID_FREQUENCIES:
        frequency = "daily"
    habit_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    try:
        client = _get_client()
        rows = [{
            "habit_id": habit_id,
            "name": name,
            "description": description,
            "frequency": frequency,
            "target_count": target_count,
            "active": True,
            "created_at": now,
        }]
        errors = client.insert_rows_json(HABITS_TABLE, rows)
        if errors:
            return {"status": "error", "error_message": str(errors)}
        return {"status": "success", "habit_id": habit_id, "name": name}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def log_habit(habit_id: str, count: int = 1, notes: Optional[str] = None) -> dict:
    """Log a habit completion for today.

    Args:
        habit_id: The UUID of the habit.
        count: Number of completions (default 1).
        notes: Optional notes.

    Returns:
        dict with 'status'.
    """
    log_id = str(uuid.uuid4())
    today = date.today().isoformat()
    now = datetime.utcnow().isoformat()
    try:
        client = _get_client()
        rows = [{
            "log_id": log_id,
            "habit_id": habit_id,
            "logged_date": today,
            "count": count,
            "notes": notes,
            "created_at": now,
        }]
        errors = client.insert_rows_json(LOGS_TABLE, rows)
        if errors:
            return {"status": "error", "error_message": str(errors)}
        return {"status": "success", "log_id": log_id, "logged_date": today}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def get_habit_streak(habit_id: str) -> dict:
    """Get the current streak and recent completions for a habit.

    Args:
        habit_id: The UUID of the habit.

    Returns:
        dict with streak_days and recent completion data.
    """
    try:
        client = _get_client()
        query = f"""
            SELECT logged_date, count
            FROM `{LOGS_TABLE}`
            WHERE habit_id = @habit_id
            ORDER BY logged_date DESC
            LIMIT 30
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("habit_id", "STRING", habit_id)]
        )
        df = client.query(query, job_config=job_config).to_dataframe()
        if df.empty:
            return {"status": "success", "streak_days": 0, "completions": []}
        completions = df.to_dict("records")
        for c in completions:
            if hasattr(c.get("logged_date"), "isoformat"):
                c["logged_date"] = c["logged_date"].isoformat()
        return {"status": "success", "streak_days": len(completions), "completions": completions}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def list_habits() -> dict:
    """List all active habits.

    Returns:
        dict with 'habits' list.
    """
    try:
        client = _get_client()
        query = f"""
            SELECT habit_id, name, description, frequency, target_count
            FROM `{HABITS_TABLE}`
            WHERE active = TRUE
            ORDER BY created_at ASC
        """
        df = client.query(query).to_dataframe()
        return {"status": "success", "habits": df.to_dict("records"), "count": len(df)}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}
