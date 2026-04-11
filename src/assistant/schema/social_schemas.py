"""Social domain BigQuery schemas."""
from google.cloud import bigquery


SOCIAL_CONTACTS = [
    bigquery.SchemaField("contact_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("relationship", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("last_contacted", "DATE", mode="NULLABLE"),
    bigquery.SchemaField("next_reminder", "DATE", mode="NULLABLE"),
    bigquery.SchemaField("notes", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
]

NEWS_PREFERENCES = [
    bigquery.SchemaField("pref_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("topic", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("frequency", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("preferred_time", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("active", "BOOL", mode="REQUIRED"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
]

SOCIAL_SCHEMAS = {
    "social_contacts": SOCIAL_CONTACTS,
    "news_preferences": NEWS_PREFERENCES,
}
