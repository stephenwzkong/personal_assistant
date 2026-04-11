"""Tools for managing finance records."""
import uuid
from datetime import datetime, date
from typing import Optional
from google.cloud import bigquery

PROJECT_ID = "gen-lang-client-0288149151"
TABLE_ID = f"{PROJECT_ID}.personal_assistant.finance_records"


def _get_client() -> bigquery.Client:
    return bigquery.Client(project=PROJECT_ID)


def add_expense(
    category: str,
    amount: float,
    description: Optional[str] = None,
    transaction_date: Optional[str] = None,
    is_recurring: bool = False,
    recurrence_period: Optional[str] = None,
) -> dict:
    """Add a new finance record (expense or income).

    Args:
        category: Category (e.g. 'food', 'rent', 'salary', 'entertainment').
        amount: Amount in dollars. Positive = income, negative = expense.
        description: Optional description.
        transaction_date: Date in YYYY-MM-DD format (defaults to today).
        is_recurring: Whether this is a recurring transaction.
        recurrence_period: 'monthly', 'weekly', etc. (if recurring).

    Returns:
        dict with 'status' and 'record_id'.
    """
    record_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    txn_date = transaction_date or date.today().isoformat()
    try:
        client = _get_client()
        rows = [{
            "record_id": record_id,
            "category": category,
            "description": description,
            "amount": amount,
            "transaction_date": txn_date,
            "is_recurring": is_recurring,
            "recurrence_period": recurrence_period,
            "created_at": now,
        }]
        errors = client.insert_rows_json(TABLE_ID, rows)
        if errors:
            return {"status": "error", "error_message": str(errors)}
        return {"status": "success", "record_id": record_id, "amount": amount, "category": category}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def get_spending_summary(period: str = "month") -> dict:
    """Get a spending summary by category for the given period.

    Args:
        period: 'week' or 'month'.

    Returns:
        dict with spending by category and totals.
    """
    period_map = {
        "week": "transaction_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)",
        "month": "transaction_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)",
    }
    condition = period_map.get(period, period_map["month"])
    try:
        client = _get_client()
        query = f"""
            SELECT
                category,
                SUM(amount) as total,
                COUNT(*) as transaction_count
            FROM `{TABLE_ID}`
            WHERE {condition}
            GROUP BY category
            ORDER BY total ASC
        """
        df = client.query(query).to_dataframe()
        breakdown = df.to_dict("records")
        total_spent = sum(r["total"] for r in breakdown if r["total"] < 0)
        total_income = sum(r["total"] for r in breakdown if r["total"] > 0)
        return {
            "status": "success",
            "period": period,
            "breakdown": breakdown,
            "total_spent": total_spent,
            "total_income": total_income,
            "net": total_income + total_spent,
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def list_recent_transactions(limit: int = 10) -> dict:
    """List recent finance transactions.

    Args:
        limit: Max number of transactions to return.

    Returns:
        dict with 'transactions' list.
    """
    limit = min(limit, 50)
    try:
        client = _get_client()
        query = f"""
            SELECT record_id, category, description, amount, transaction_date, is_recurring
            FROM `{TABLE_ID}`
            ORDER BY transaction_date DESC, created_at DESC
            LIMIT {limit}
        """
        df = client.query(query).to_dataframe()
        txns = df.to_dict("records")
        for t in txns:
            if hasattr(t.get("transaction_date"), "isoformat"):
                t["transaction_date"] = t["transaction_date"].isoformat()
        return {"status": "success", "transactions": txns, "count": len(txns)}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}
