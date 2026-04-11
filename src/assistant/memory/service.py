"""MemoryService — read/write user facts and build memory bundles for prompts.

Phase 1: SQL-only retrieval. No embeddings, no episodic memory yet.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional
from google.cloud import bigquery


PROJECT_ID = "gen-lang-client-0288149151"
DATASET = "personal_assistant"
FACTS_TABLE = f"{PROJECT_ID}.{DATASET}.memory_facts"
SESSIONS_TABLE = f"{PROJECT_ID}.{DATASET}.memory_sessions"

VALID_CATEGORIES = {
    "preference", "profile", "relationship", "goal", "constraint", "location", "routine",
}

# Token budget for the injected memory block (rough chars per token = 4)
MAX_BUNDLE_CHARS = 1600  # ~400 tokens
DEFAULT_RECALL_LIMIT = 20


def _client() -> bigquery.Client:
    return bigquery.Client(project=PROJECT_ID)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def save_memory(
    user_id: str,
    category: str,
    subject: str,
    value: str,
    predicate: Optional[str] = None,
    confidence: float = 0.9,
    source_agent: Optional[str] = None,
    source_session: Optional[str] = None,
    ttl_days: Optional[int] = None,
) -> dict:
    """Persist (or upsert) a single fact about the user.

    Uses MERGE on (user_id, subject) to avoid duplicates.
    """
    if category not in VALID_CATEGORIES:
        category = "preference"

    fact_id = str(uuid.uuid4())
    now = _now_iso()

    merge_sql = f"""
    MERGE `{FACTS_TABLE}` T
    USING (
      SELECT
        @fact_id AS fact_id,
        @user_id AS user_id,
        @category AS category,
        @subject AS subject,
        @predicate AS predicate,
        @value AS value,
        @source_agent AS source_agent,
        @source_session AS source_session,
        @confidence AS confidence,
        @ttl_days AS ttl_days,
        TIMESTAMP(@now) AS now_ts
    ) S
    ON T.user_id = S.user_id AND T.subject = S.subject
    WHEN MATCHED THEN UPDATE SET
      value = S.value,
      predicate = S.predicate,
      category = S.category,
      confidence = S.confidence,
      source_agent = S.source_agent,
      source_session = S.source_session,
      updated_at = S.now_ts
    WHEN NOT MATCHED THEN INSERT (
      fact_id, user_id, category, subject, predicate, value,
      source_agent, source_session, confidence, ttl_days,
      created_at, updated_at, last_accessed_at, access_count
    ) VALUES (
      S.fact_id, S.user_id, S.category, S.subject, S.predicate, S.value,
      S.source_agent, S.source_session, S.confidence, S.ttl_days,
      S.now_ts, S.now_ts, NULL, 0
    )
    """

    params = [
        bigquery.ScalarQueryParameter("fact_id", "STRING", fact_id),
        bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
        bigquery.ScalarQueryParameter("category", "STRING", category),
        bigquery.ScalarQueryParameter("subject", "STRING", subject),
        bigquery.ScalarQueryParameter("predicate", "STRING", predicate),
        bigquery.ScalarQueryParameter("value", "STRING", value),
        bigquery.ScalarQueryParameter("source_agent", "STRING", source_agent),
        bigquery.ScalarQueryParameter("source_session", "STRING", source_session),
        bigquery.ScalarQueryParameter("confidence", "FLOAT64", confidence),
        bigquery.ScalarQueryParameter("ttl_days", "INT64", ttl_days),
        bigquery.ScalarQueryParameter("now", "STRING", now),
    ]

    try:
        _client().query(merge_sql, job_config=bigquery.QueryJobConfig(query_parameters=params)).result()
        return {"status": "success", "subject": subject, "value": value}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def recall_memory(
    user_id: str,
    query: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 10,
) -> dict:
    """Retrieve facts about the user, optionally filtered by category or keyword.

    Phase 1: SQL keyword search on subject + value. No embeddings.
    """
    conditions = ["user_id = @user_id"]
    params = [bigquery.ScalarQueryParameter("user_id", "STRING", user_id)]

    if category and category in VALID_CATEGORIES:
        conditions.append("category = @category")
        params.append(bigquery.ScalarQueryParameter("category", "STRING", category))

    if query:
        conditions.append("(LOWER(subject) LIKE @q OR LOWER(value) LIKE @q)")
        params.append(bigquery.ScalarQueryParameter("q", "STRING", f"%{query.lower()}%"))

    where = " AND ".join(conditions)
    sql = f"""
        SELECT category, subject, predicate, value, confidence,
               source_agent, created_at, updated_at
        FROM `{FACTS_TABLE}`
        WHERE {where}
        ORDER BY confidence DESC, updated_at DESC
        LIMIT {int(limit)}
    """

    try:
        rows = _client().query(sql, job_config=bigquery.QueryJobConfig(query_parameters=params)).result()
        facts = []
        for r in rows:
            facts.append({
                "category": r["category"],
                "subject": r["subject"],
                "predicate": r["predicate"],
                "value": r["value"],
                "confidence": r["confidence"],
            })
        return {"status": "success", "facts": facts, "count": len(facts)}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def forget_memory(user_id: str, subject: str) -> dict:
    """Delete a fact by subject."""
    sql = f"DELETE FROM `{FACTS_TABLE}` WHERE user_id = @user_id AND subject = @subject"
    params = [
        bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
        bigquery.ScalarQueryParameter("subject", "STRING", subject),
    ]
    try:
        _client().query(sql, job_config=bigquery.QueryJobConfig(query_parameters=params)).result()
        return {"status": "success", "subject": subject}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def build_bundle(user_id: str, max_facts: int = DEFAULT_RECALL_LIMIT) -> str:
    """Build a compact natural-language memory block to inject into the system prompt.

    Returns an empty string if no memories exist (so callers can skip injection).
    """
    result = recall_memory(user_id=user_id, limit=max_facts)
    if result.get("status") != "success" or not result.get("facts"):
        return ""

    # Group by category for compact rendering
    by_cat: dict[str, list[str]] = {}
    for f in result["facts"]:
        line = f"{f['subject']}: {f['value']}"
        by_cat.setdefault(f["category"], []).append(line)

    parts: list[str] = ["<user_memory>"]
    for cat, lines in by_cat.items():
        parts.append(f"  [{cat}]")
        for ln in lines:
            parts.append(f"    - {ln}")
    parts.append("</user_memory>")

    bundle = "\n".join(parts)
    if len(bundle) > MAX_BUNDLE_CHARS:
        bundle = bundle[:MAX_BUNDLE_CHARS] + "\n...</user_memory>"
    return bundle


def record_session_start(session_id: str, user_id: str) -> None:
    """Insert a session row at session start (idempotent best-effort)."""
    sql = f"""
    MERGE `{SESSIONS_TABLE}` T
    USING (SELECT @session_id AS session_id, @user_id AS user_id, TIMESTAMP(@now) AS now_ts) S
    ON T.session_id = S.session_id
    WHEN NOT MATCHED THEN INSERT (session_id, user_id, started_at, message_count)
    VALUES (S.session_id, S.user_id, S.now_ts, 0)
    """
    params = [
        bigquery.ScalarQueryParameter("session_id", "STRING", session_id),
        bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
        bigquery.ScalarQueryParameter("now", "STRING", _now_iso()),
    ]
    try:
        _client().query(sql, job_config=bigquery.QueryJobConfig(query_parameters=params)).result()
    except Exception:
        pass  # non-critical
