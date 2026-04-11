"""Shared schemas used across domains."""
from google.cloud import bigquery


CALENDAR_EVENTS = [
    bigquery.SchemaField("event_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("title", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("start_datetime", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("end_datetime", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("event_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("source_agent", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("priority", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("status", "STRING", mode="REQUIRED"),  # active|cancelled|completed
    bigquery.SchemaField("description", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("metadata", "JSON", mode="NULLABLE"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
]

TRIVIAL_TASKS = [
    bigquery.SchemaField("task_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("title", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("category", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("due_date", "TIMESTAMP", mode="NULLABLE"),
    bigquery.SchemaField("priority", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("status", "STRING", mode="REQUIRED"),  # pending|done|deferred
    bigquery.SchemaField("notes", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
]

SHARED_SCHEMAS = {
    "calendar_events": CALENDAR_EVENTS,
    "trivial_tasks": TRIVIAL_TASKS,
}
