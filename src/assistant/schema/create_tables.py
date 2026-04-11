"""Provision all BigQuery tables for the personal assistant."""
from google.cloud import bigquery
from schema.shared_schemas import SHARED_SCHEMAS
from schema.wellness_schemas import WELLNESS_SCHEMAS
from schema.productivity_schemas import PRODUCTIVITY_SCHEMAS
from schema.social_schemas import SOCIAL_SCHEMAS
from schema.finance_schemas import FINANCE_SCHEMAS
from schema.memory_schemas import MEMORY_SCHEMAS

PROJECT_ID = "gen-lang-client-0288149151"
DATASET = "personal_assistant"

client = bigquery.Client(project=PROJECT_ID)


def create_table(table_id: str, schema: list, description: str = ""):
    full_id = f"{PROJECT_ID}.{DATASET}.{table_id}"
    table = bigquery.Table(full_id, schema=schema)
    if description:
        table.description = description
    table = client.create_table(table, exists_ok=True)
    print(f"  {table.project}.{table.dataset_id}.{table.table_id}")
    return table


# Combine all domain schemas
TABLES = {
    **SHARED_SCHEMAS,
    **WELLNESS_SCHEMAS,
    **PRODUCTIVITY_SCHEMAS,
    **SOCIAL_SCHEMAS,
    **FINANCE_SCHEMAS,
    **MEMORY_SCHEMAS,
}


if __name__ == "__main__":
    print(f"Creating tables in {PROJECT_ID}.{DATASET}...")
    for table_name, schema in TABLES.items():
        create_table(table_name, schema)
    print("Done.")
