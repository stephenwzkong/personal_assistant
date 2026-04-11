"""Read-only tools for querying the existing fitness_tracker BigQuery table."""
from typing import Optional
from google.cloud import bigquery

PROJECT_ID = "gen-lang-client-0288149151"
TABLE_ID = f"{PROJECT_ID}.personal_assistant.fitness_tracker"


def _get_client() -> bigquery.Client:
    return bigquery.Client(project=PROJECT_ID)


def get_recent_workouts(limit: int = 10) -> dict:
    """Get the most recent workout records.

    Args:
        limit: Number of recent workouts to return (default 10, max 50).

    Returns:
        dict with 'status' and 'workouts' list or 'error_message'.
    """
    limit = min(limit, 50)
    try:
        client = _get_client()
        query = f"""
            SELECT workout_timestamp, exercise_type, duration_hours, duration_minutes,
                   calories_burned, notes
            FROM `{TABLE_ID}`
            ORDER BY workout_timestamp DESC
            LIMIT {limit}
        """
        df = client.query(query).to_dataframe()
        workouts = df.to_dict("records")
        for w in workouts:
            if hasattr(w.get("workout_timestamp"), "isoformat"):
                w["workout_timestamp"] = w["workout_timestamp"].isoformat()
        return {"status": "success", "workouts": workouts, "count": len(workouts)}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def get_workout_stats(period: str = "week") -> dict:
    """Get aggregated workout statistics for a given period.

    Args:
        period: 'today', 'week', or 'month'.

    Returns:
        dict with total hours, calories, and session count.
    """
    period_map = {
        "today": "DATE(workout_timestamp) = CURRENT_DATE()",
        "week": "DATE(workout_timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)",
        "month": "DATE(workout_timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)",
    }
    condition = period_map.get(period, period_map["week"])
    try:
        client = _get_client()
        query = f"""
            SELECT
                COUNT(*) as session_count,
                COALESCE(SUM(duration_hours), 0) as total_hours,
                COALESCE(SUM(calories_burned), 0) as total_calories,
                ARRAY_AGG(DISTINCT exercise_type IGNORE NULLS) as exercise_types
            FROM `{TABLE_ID}`
            WHERE {condition}
        """
        df = client.query(query).to_dataframe()
        if df.empty:
            return {"status": "success", "session_count": 0, "total_hours": 0,
                    "total_calories": 0, "exercise_types": []}
        row = df.iloc[0].to_dict()
        row["total_hours"] = float(row["total_hours"])
        row["total_calories"] = int(row["total_calories"])
        row["session_count"] = int(row["session_count"])
        return {"status": "success", **row}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def get_workouts_by_type(exercise_type: str, limit: int = 10) -> dict:
    """Get workouts filtered by exercise type.

    Args:
        exercise_type: Type of exercise (e.g. Running, Cycling, Strength Training).
        limit: Max number of records to return.

    Returns:
        dict with 'status' and 'workouts' list.
    """
    limit = min(limit, 50)
    try:
        client = _get_client()
        query = f"""
            SELECT workout_timestamp, exercise_type, duration_hours, duration_minutes,
                   calories_burned, notes
            FROM `{TABLE_ID}`
            WHERE LOWER(exercise_type) = LOWER(@exercise_type)
            ORDER BY workout_timestamp DESC
            LIMIT {limit}
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("exercise_type", "STRING", exercise_type)
            ]
        )
        df = client.query(query, job_config=job_config).to_dataframe()
        workouts = df.to_dict("records")
        for w in workouts:
            if hasattr(w.get("workout_timestamp"), "isoformat"):
                w["workout_timestamp"] = w["workout_timestamp"].isoformat()
        return {"status": "success", "workouts": workouts, "count": len(workouts)}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}
