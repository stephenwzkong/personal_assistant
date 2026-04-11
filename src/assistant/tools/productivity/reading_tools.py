"""Tools for managing the reading list."""
import uuid
from datetime import datetime
from typing import Optional
from google.cloud import bigquery

PROJECT_ID = "gen-lang-client-0288149151"
TABLE_ID = f"{PROJECT_ID}.personal_assistant.reading_list"

VALID_STATUSES = ["to_read", "reading", "completed"]


def _get_client() -> bigquery.Client:
    return bigquery.Client(project=PROJECT_ID)


def add_book(
    title: str,
    author: Optional[str] = None,
    total_pages: Optional[int] = None,
    notes: Optional[str] = None,
) -> dict:
    """Add a book to the reading list.

    Args:
        title: Book title.
        author: Author name.
        total_pages: Total number of pages.
        notes: Optional notes about the book.

    Returns:
        dict with 'status' and 'book_id'.
    """
    book_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    try:
        client = _get_client()
        rows = [{
            "book_id": book_id,
            "title": title,
            "author": author,
            "status": "to_read",
            "current_page": 0,
            "total_pages": total_pages,
            "notes": notes,
            "created_at": now,
            "updated_at": now,
        }]
        errors = client.insert_rows_json(TABLE_ID, rows)
        if errors:
            return {"status": "error", "error_message": str(errors)}
        return {"status": "success", "book_id": book_id, "title": title}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def update_reading_progress(
    book_id: str,
    current_page: int,
    status: Optional[str] = None,
) -> dict:
    """Update reading progress for a book.

    Args:
        book_id: The UUID of the book.
        current_page: Current page number.
        status: Optional new status: to_read, reading, or completed.

    Returns:
        dict with 'status'.
    """
    if status and status not in VALID_STATUSES:
        return {"status": "error", "error_message": f"Invalid status. Use: {VALID_STATUSES}"}

    try:
        client = _get_client()
        now = datetime.utcnow().isoformat()
        status_set = ", status = @status" if status else ""
        params = [
            bigquery.ScalarQueryParameter("book_id", "STRING", book_id),
            bigquery.ScalarQueryParameter("current_page", "INT64", current_page),
            bigquery.ScalarQueryParameter("now", "STRING", now),
        ]
        if status:
            params.append(bigquery.ScalarQueryParameter("status", "STRING", status))

        query = f"""
            UPDATE `{TABLE_ID}`
            SET current_page = @current_page, updated_at = @now{status_set}
            WHERE book_id = @book_id
        """
        client.query(query, job_config=bigquery.QueryJobConfig(query_parameters=params)).result()
        return {"status": "success", "book_id": book_id, "current_page": current_page}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def list_books(status: Optional[str] = None) -> dict:
    """List books in the reading list.

    Args:
        status: Filter by status: to_read, reading, or completed (optional).

    Returns:
        dict with 'books' list.
    """
    try:
        client = _get_client()
        conditions = ["1=1"]
        params = []
        if status and status in VALID_STATUSES:
            conditions.append("status = @status")
            params.append(bigquery.ScalarQueryParameter("status", "STRING", status))

        query = f"""
            SELECT book_id, title, author, status, current_page, total_pages, notes
            FROM `{TABLE_ID}`
            WHERE {" AND ".join(conditions)}
            ORDER BY
                CASE status WHEN 'reading' THEN 1 WHEN 'to_read' THEN 2 ELSE 3 END,
                updated_at DESC
        """
        job_config = bigquery.QueryJobConfig(query_parameters=params)
        df = client.query(query, job_config=job_config).to_dataframe()
        return {"status": "success", "books": df.to_dict("records"), "count": len(df)}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}
