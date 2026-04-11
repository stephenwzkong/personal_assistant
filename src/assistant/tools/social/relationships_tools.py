"""Tools for managing social contacts and reminders."""
import uuid
from datetime import datetime, date
from typing import Optional
from google.cloud import bigquery

PROJECT_ID = "gen-lang-client-0288149151"
TABLE_ID = f"{PROJECT_ID}.personal_assistant.social_contacts"


def _get_client() -> bigquery.Client:
    return bigquery.Client(project=PROJECT_ID)


def add_contact(
    name: str,
    relationship: Optional[str] = None,
    notes: Optional[str] = None,
    next_reminder: Optional[str] = None,
) -> dict:
    """Add a new social contact.

    Args:
        name: Contact's name.
        relationship: Relationship type (e.g. 'friend', 'family', 'colleague').
        notes: Optional notes about the person.
        next_reminder: Date to be reminded to reach out (YYYY-MM-DD).

    Returns:
        dict with 'status' and 'contact_id'.
    """
    contact_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    try:
        client = _get_client()
        rows = [{
            "contact_id": contact_id,
            "name": name,
            "relationship": relationship,
            "last_contacted": None,
            "next_reminder": next_reminder,
            "notes": notes,
            "created_at": now,
            "updated_at": now,
        }]
        errors = client.insert_rows_json(TABLE_ID, rows)
        if errors:
            return {"status": "error", "error_message": str(errors)}
        return {"status": "success", "contact_id": contact_id, "name": name}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def log_contact(contact_id: str, next_reminder: Optional[str] = None) -> dict:
    """Log that you contacted someone and optionally set a next reminder.

    Args:
        contact_id: The UUID of the contact.
        next_reminder: Next reminder date in YYYY-MM-DD format.

    Returns:
        dict with 'status'.
    """
    try:
        client = _get_client()
        today = date.today().isoformat()
        now = datetime.utcnow().isoformat()
        params = [
            bigquery.ScalarQueryParameter("contact_id", "STRING", contact_id),
            bigquery.ScalarQueryParameter("today", "STRING", today),
            bigquery.ScalarQueryParameter("now", "STRING", now),
        ]
        reminder_set = ""
        if next_reminder:
            params.append(bigquery.ScalarQueryParameter("next_reminder", "STRING", next_reminder))
            reminder_set = ", next_reminder = @next_reminder"

        query = f"""
            UPDATE `{TABLE_ID}`
            SET last_contacted = @today, updated_at = @now{reminder_set}
            WHERE contact_id = @contact_id
        """
        client.query(query, job_config=bigquery.QueryJobConfig(query_parameters=params)).result()
        return {"status": "success", "contact_id": contact_id, "last_contacted": today}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def get_contacts_to_reach_out() -> dict:
    """Get contacts whose reminder date is today or overdue.

    Returns:
        dict with 'contacts' list.
    """
    try:
        client = _get_client()
        query = f"""
            SELECT contact_id, name, relationship, last_contacted, next_reminder, notes
            FROM `{TABLE_ID}`
            WHERE next_reminder IS NOT NULL AND next_reminder <= CURRENT_DATE()
            ORDER BY next_reminder ASC
        """
        df = client.query(query).to_dataframe()
        contacts = df.to_dict("records")
        for c in contacts:
            for k in ("last_contacted", "next_reminder"):
                if hasattr(c.get(k), "isoformat"):
                    c[k] = c[k].isoformat()
        return {"status": "success", "contacts": contacts, "count": len(contacts)}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def list_contacts(limit: int = 20) -> dict:
    """List all contacts.

    Args:
        limit: Max number of contacts to return.

    Returns:
        dict with 'contacts' list.
    """
    try:
        client = _get_client()
        query = f"""
            SELECT contact_id, name, relationship, last_contacted, next_reminder, notes
            FROM `{TABLE_ID}`
            ORDER BY name ASC
            LIMIT {limit}
        """
        df = client.query(query).to_dataframe()
        contacts = df.to_dict("records")
        for c in contacts:
            for k in ("last_contacted", "next_reminder"):
                if hasattr(c.get(k), "isoformat"):
                    c[k] = c[k].isoformat()
        return {"status": "success", "contacts": contacts, "count": len(contacts)}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}
