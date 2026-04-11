"""Read-only tools for querying the existing meal_hour BigQuery table."""
from google.cloud import bigquery

PROJECT_ID = "gen-lang-client-0288149151"
TABLE_ID = f"{PROJECT_ID}.personal_assistant.meal_hour"


def _get_client() -> bigquery.Client:
    return bigquery.Client(project=PROJECT_ID)


def get_recent_meals(limit: int = 10) -> dict:
    """Get the most recent meal records.

    Args:
        limit: Number of recent meals to return (default 10, max 50).

    Returns:
        dict with 'status' and 'meals' list or 'error_message'.
    """
    limit = min(limit, 50)
    try:
        client = _get_client()
        query = f"""
            SELECT *
            FROM `{TABLE_ID}`
            ORDER BY created_at DESC
            LIMIT {limit}
        """
        df = client.query(query).to_dataframe()
        meals = df.to_dict("records")
        for m in meals:
            for k, v in m.items():
                if hasattr(v, "isoformat"):
                    m[k] = v.isoformat()
        return {"status": "success", "meals": meals, "count": len(meals)}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def get_meal_summary(period: str = "today") -> dict:
    """Get aggregated meal/nutrition summary for today or this week.

    Args:
        period: 'today' or 'week'.

    Returns:
        dict with aggregated nutrition data.
    """
    period_map = {
        "today": "DATE(created_at) = CURRENT_DATE()",
        "week": "DATE(created_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)",
    }
    condition = period_map.get(period, period_map["today"])
    try:
        client = _get_client()
        # Query to get summary - schema may vary, so use a flexible approach
        query = f"""
            SELECT COUNT(*) as meal_count
            FROM `{TABLE_ID}`
            WHERE {condition}
        """
        df = client.query(query).to_dataframe()
        if df.empty:
            return {"status": "success", "meal_count": 0, "period": period}
        row = df.iloc[0].to_dict()
        row["period"] = period
        return {"status": "success", **row}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def get_eating_window_today() -> dict:
    """Get today's first and last meal times to determine the eating window.

    Returns:
        dict with first_meal, last_meal, and window_hours.
    """
    try:
        client = _get_client()
        query = f"""
            SELECT
                MIN(created_at) as first_meal,
                MAX(created_at) as last_meal,
                TIMESTAMP_DIFF(MAX(created_at), MIN(created_at), HOUR) as window_hours
            FROM `{TABLE_ID}`
            WHERE DATE(created_at) = CURRENT_DATE()
        """
        df = client.query(query).to_dataframe()
        if df.empty or df["first_meal"].isna().all():
            return {"status": "success", "message": "No meals recorded today"}
        row = df.iloc[0].to_dict()
        for k in ("first_meal", "last_meal"):
            if hasattr(row.get(k), "isoformat"):
                row[k] = row[k].isoformat()
        return {"status": "success", **row}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}
