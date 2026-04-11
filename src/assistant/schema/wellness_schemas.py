"""Wellness domain BigQuery schemas."""
from google.cloud import bigquery


HABITS = [
    bigquery.SchemaField("habit_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("description", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("frequency", "STRING", mode="REQUIRED"),  # daily|weekdays|weekly
    bigquery.SchemaField("target_count", "INT64", mode="REQUIRED"),
    bigquery.SchemaField("active", "BOOL", mode="REQUIRED"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
]

HABIT_LOGS = [
    bigquery.SchemaField("log_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("habit_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("logged_date", "DATE", mode="REQUIRED"),
    bigquery.SchemaField("count", "INT64", mode="REQUIRED"),
    bigquery.SchemaField("notes", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
]

WELLNESS_SCHEMAS = {
    "habits": HABITS,
    "habit_logs": HABIT_LOGS,
}
