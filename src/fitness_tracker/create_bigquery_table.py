"""Create BigQuery table for fitness tracker."""
from google.cloud import bigquery

# Initialize BigQuery client
client = bigquery.Client(project="gen-lang-client-0288149151")

# Define table schema
schema = [
    bigquery.SchemaField("workout_timestamp", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("exercise_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("duration_hours", "FLOAT64", mode="REQUIRED"),
    bigquery.SchemaField("duration_minutes", "INT64", mode="REQUIRED"),
    bigquery.SchemaField("calories_burned", "INT64", mode="REQUIRED"),
    bigquery.SchemaField("notes", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("image_uri", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
]

# Define table ID
table_id = "gen-lang-client-0288149151.personal_assistant.fitness_tracker"

# Create table
table = bigquery.Table(table_id, schema=schema)
table = client.create_table(table, exists_ok=True)

print(f"✅ Created table {table.project}.{table.dataset_id}.{table.table_id}")
print(f"   Schema: {len(table.schema)} fields")
for field in table.schema:
    print(f"   - {field.name}: {field.field_type}")
