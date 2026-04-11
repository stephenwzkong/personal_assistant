"""BigQuery schemas for the memory system (Phase 1: facts + sessions)."""
from google.cloud import bigquery


# Atomic facts about the user (preferences, profile, goals, constraints)
MEMORY_FACTS = [
    bigquery.SchemaField("fact_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("category", "STRING", mode="REQUIRED"),
    # e.g. "preference", "profile", "relationship", "goal", "constraint", "location"
    bigquery.SchemaField("subject", "STRING", mode="REQUIRED"),
    # dotted-path identifier, e.g. "user.workout.preferred_time"
    bigquery.SchemaField("predicate", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("value", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("source_agent", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("source_session", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("confidence", "FLOAT64", mode="NULLABLE"),
    bigquery.SchemaField("ttl_days", "INT64", mode="NULLABLE"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("last_accessed_at", "TIMESTAMP", mode="NULLABLE"),
    bigquery.SchemaField("access_count", "INT64", mode="NULLABLE"),
]


# Per-session conversational digest (one row per session)
MEMORY_SESSIONS = [
    bigquery.SchemaField("session_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("started_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("ended_at", "TIMESTAMP", mode="NULLABLE"),
    bigquery.SchemaField("message_count", "INT64", mode="NULLABLE"),
    bigquery.SchemaField("summary", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("topics", "STRING", mode="REPEATED"),
    bigquery.SchemaField("agents_used", "STRING", mode="REPEATED"),
]


MEMORY_SCHEMAS = {
    "memory_facts": MEMORY_FACTS,
    "memory_sessions": MEMORY_SESSIONS,
}
