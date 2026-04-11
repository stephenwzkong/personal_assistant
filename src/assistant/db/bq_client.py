"""Shared BigQuery query wrapper for calendar events."""
from datetime import datetime, timedelta
from typing import Optional
from google.cloud import bigquery

PROJECT_ID = "gen-lang-client-0288149151"
DATASET = "personal_assistant"
CALENDAR_TABLE = f"{PROJECT_ID}.{DATASET}.calendar_events"


def _get_client() -> bigquery.Client:
    return bigquery.Client(project=PROJECT_ID)


def query_calendar_events(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> list[dict]:
    """Query active calendar events in a date range for the UI.

    Args:
        start_date: Start date YYYY-MM-DD (defaults to today - 7 days).
        end_date: End date YYYY-MM-DD (defaults to today + 35 days for 6-week view).

    Returns:
        List of event dicts with color added.
    """
    from tools.shared.calendar_tools import EVENT_COLORS

    today = datetime.utcnow().date()
    if not start_date:
        # Start from most recent Monday
        days_back = today.weekday()
        start_date = (today - timedelta(days=days_back)).isoformat()
    if not end_date:
        end_date = (today + timedelta(days=42)).isoformat()  # 6 weeks forward

    try:
        client = _get_client()
        query = f"""
            SELECT
                event_id,
                title,
                start_datetime,
                end_datetime,
                event_type,
                source_agent,
                priority,
                status,
                description
            FROM `{CALENDAR_TABLE}`
            WHERE status = 'active'
              AND DATE(start_datetime) >= '{start_date}'
              AND DATE(start_datetime) <= '{end_date}'
            ORDER BY start_datetime ASC
            LIMIT 500
        """
        df = client.query(query).to_dataframe()
        events = []
        for _, row in df.iterrows():
            event = row.to_dict()
            # Serialize timestamps
            for k in ("start_datetime", "end_datetime"):
                if hasattr(event[k], "isoformat"):
                    event[k] = event[k].isoformat()
            # Add display color
            event["color"] = EVENT_COLORS.get(event.get("event_type", "other"), "#94A3B8")
            # Add date-only string for grouping
            event["date"] = event["start_datetime"][:10] if event["start_datetime"] else ""
            # Add short time
            if event["start_datetime"] and len(event["start_datetime"]) >= 16:
                event["time"] = event["start_datetime"][11:16]
            else:
                event["time"] = ""
            events.append(event)
        return events
    except Exception:
        return []


def get_week_start(reference_date: Optional[str] = None) -> str:
    """Get the Monday of the week containing reference_date.

    Args:
        reference_date: Date string YYYY-MM-DD (defaults to today).

    Returns:
        ISO date string for the Monday of that week.
    """
    if reference_date:
        d = datetime.strptime(reference_date, "%Y-%m-%d").date()
    else:
        d = datetime.utcnow().date()
    monday = d - timedelta(days=d.weekday())
    return monday.isoformat()
