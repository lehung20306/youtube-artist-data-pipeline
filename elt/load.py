import logging

from google.cloud import bigquery

logger = logging.getLogger(__name__)

def load_data_to_bigquery(json_data: list, table_id: str, write_disposition: str="WRITE_TRUNCATE"):
    if not json_data:
        logger.warning(f"No data to load into {table_id}. Skipping load operation.")
        return
    
    client = bigquery.Client()

    job_config = bigquery.LoadJobConfig(
        write_disposition=write_disposition,
        autodetect=True,
    )

    try:
        job = client.load_table_from_json(json_data, table_id, job_config=job_config)
        job.result()  # Wait for the job to complete
        logger.info(f"Loaded {job.output_rows} rows into {table_id}.")
    except Exception as e:
        logger.error(f"Failed to load data into {table_id}: {e}")
        raise

if __name__ == "__main__":
    print(1)
