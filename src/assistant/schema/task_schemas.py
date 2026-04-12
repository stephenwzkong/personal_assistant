"""Task / to-do BigQuery schemas."""
from google.cloud import bigquery

TASKS = [
    bigquery.SchemaField("task_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("parent_task_id", "STRING", mode="NULLABLE"),  # links sub-steps to parent
    bigquery.SchemaField("title", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("description", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("status", "STRING", mode="REQUIRED"),  # todo | in_progress | done
    bigquery.SchemaField("priority", "STRING", mode="NULLABLE"),  # low | medium | high
    bigquery.SchemaField("category", "STRING", mode="NULLABLE"),  # e.g. school, fitness, finance
    bigquery.SchemaField("due_date", "DATE", mode="NULLABLE"),
    bigquery.SchemaField("position", "INT64", mode="REQUIRED"),  # ordering within a column
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
]

TASK_SCHEMAS = {
    "tasks": TASKS,
}
