"""Tools for managing news preferences and fetching summaries."""
import uuid
from datetime import datetime
from typing import Optional
from google.cloud import bigquery

PROJECT_ID = "gen-lang-client-0288149151"
TABLE_ID = f"{PROJECT_ID}.personal_assistant.news_preferences"


def _get_client() -> bigquery.Client:
    return bigquery.Client(project=PROJECT_ID)


def add_news_topic(
    topic: str,
    frequency: str = "daily",
    preferred_time: Optional[str] = None,
) -> dict:
    """Add a news topic preference.

    Args:
        topic: News topic (e.g. 'AI technology', 'finance', 'sports', 'local news').
        frequency: How often to get updates: 'daily', 'weekly'.
        preferred_time: Preferred time to receive news (HH:MM format).

    Returns:
        dict with 'status' and 'pref_id'.
    """
    pref_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    try:
        client = _get_client()
        rows = [{
            "pref_id": pref_id,
            "topic": topic,
            "frequency": frequency,
            "preferred_time": preferred_time,
            "active": True,
            "created_at": now,
        }]
        errors = client.insert_rows_json(TABLE_ID, rows)
        if errors:
            return {"status": "error", "error_message": str(errors)}
        return {"status": "success", "pref_id": pref_id, "topic": topic}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def get_news_preferences() -> dict:
    """Get all active news topic preferences.

    Returns:
        dict with 'preferences' list.
    """
    try:
        client = _get_client()
        query = f"""
            SELECT pref_id, topic, frequency, preferred_time
            FROM `{TABLE_ID}`
            WHERE active = TRUE
            ORDER BY created_at ASC
        """
        df = client.query(query).to_dataframe()
        return {"status": "success", "preferences": df.to_dict("records"), "count": len(df)}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def get_news_briefing(topics: Optional[list] = None) -> dict:
    """Generate a news briefing summary for the given topics using the model's knowledge.

    Args:
        topics: List of topics to cover. If None, uses stored preferences.

    Returns:
        dict with briefing prompt for the LLM to generate.
    """
    if not topics:
        prefs = get_news_preferences()
        topics = [p["topic"] for p in prefs.get("preferences", [])]

    if not topics:
        topics = ["general news", "technology", "world events"]

    return {
        "status": "success",
        "topics": topics,
        "instruction": (
            f"Generate a concise news briefing covering these topics: {', '.join(topics)}. "
            "Provide 2-3 key points per topic. Note: This uses model knowledge and may not "
            "reflect the very latest news."
        ),
    }
