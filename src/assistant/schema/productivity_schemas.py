"""Productivity domain BigQuery schemas."""
from google.cloud import bigquery


READING_LIST = [
    bigquery.SchemaField("book_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("title", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("author", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("status", "STRING", mode="REQUIRED"),  # to_read|reading|completed
    bigquery.SchemaField("current_page", "INT64", mode="NULLABLE"),
    bigquery.SchemaField("total_pages", "INT64", mode="NULLABLE"),
    bigquery.SchemaField("notes", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
]

SCHOOL_ASSIGNMENTS = [
    bigquery.SchemaField("assignment_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("course", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("title", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("due_date", "TIMESTAMP", mode="NULLABLE"),
    bigquery.SchemaField("priority", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("status", "STRING", mode="REQUIRED"),  # pending|in_progress|submitted|graded
    bigquery.SchemaField("description", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("grade", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
]

LONG_TERM_GOALS = [
    bigquery.SchemaField("goal_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("title", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("category", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("description", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("target_date", "DATE", mode="NULLABLE"),
    bigquery.SchemaField("status", "STRING", mode="REQUIRED"),  # active|paused|completed
    bigquery.SchemaField("milestones", "JSON", mode="NULLABLE"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
]

PRODUCTIVITY_SCHEMAS = {
    "reading_list": READING_LIST,
    "school_assignments": SCHOOL_ASSIGNMENTS,
    "long_term_goals": LONG_TERM_GOALS,
}
