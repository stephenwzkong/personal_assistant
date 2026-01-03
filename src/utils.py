from google.cloud import bigquery

def run_bigquery_query(
    project_id: Optional[str] = GOOGLE_CLOUD_PROJECT
) -> pd.DataFrame:
    """
    Execute a BigQuery SQL query and return results as a pandas DataFrame.
    
    Args:
        query (str): The SQL query to execute
        project_id (Optional[str]): Google Cloud project ID. If None, uses GOOGLE_CLOUD_PROJECT env var or default credentials
        use_legacy_sql (bool): Whether to use legacy SQL syntax (default: False, uses standard SQL)
        max_results (Optional[int]): Maximum number of rows to return (None = return all)
        return_dataframe (bool): If True, returns pandas DataFrame; if False, returns raw query job result
    
    Returns:
        pd.DataFrame: Query results as a pandas DataFrame
    
    Example:
        >>> df = run_bigquery_query(
        ...     "SELECT name, age FROM `my-project.my_dataset.my_table` LIMIT 10",
        ...     project_id="my-project"
        ... )
        >>> print(df.head())
    """
    
    # Initialize BigQuery client
    client = bigquery.Client(project=project_id)
    
    # Configure query job
    job_config = bigquery.QueryJobConfig()
    
    # Execute query
    try:
        query = """
         SELECT * FROM `gen-lang-client-0288149151.personal_assistant.meal_hour`
         """
        query_job = client.query(query, job_config=job_config)
        
        # Wait for the query to complete
        query_job.result()
        
        # Check for errors
        if query_job.errors:
            raise Exception(f"Query failed with errors: {query_job.errors}")
        
        # Get results
        results = query_job.to_dataframe()

        return results
    

    except Exception as e:
        raise Exception(f"Error executing BigQuery query: {e}")

#df = run_bigquery_query(
#    project_id=project_id
#)