"""Finance domain BigQuery schemas."""
from google.cloud import bigquery


FINANCE_RECORDS = [
    bigquery.SchemaField("record_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("category", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("description", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("amount", "FLOAT64", mode="REQUIRED"),
    bigquery.SchemaField("transaction_date", "DATE", mode="REQUIRED"),
    bigquery.SchemaField("is_recurring", "BOOL", mode="REQUIRED"),
    bigquery.SchemaField("recurrence_period", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
]

FINANCE_SCHEMAS = {
    "finance_records": FINANCE_RECORDS,
}
