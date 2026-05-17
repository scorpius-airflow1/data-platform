from datetime import datetime
from airflow.sdk import dag, task
from tasks.ingest.download_kaggle import verify_file_in_s3, log_ingestion

S3_KEY = "raw/supply_chain/supply_chain_data.csv"
DATASET_NAME = "supply_chain"


@dag(
    dag_id="ingest_supply_chain",
    description="Verifica y registra ingestión de Supply Chain Dataset en S3 raw/",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["ingesta", "supply_chain", "raw"],
    default_args={"queue": "default"},
)
def ingest_supply_chain():

    @task()
    def verify() -> str:
        """Verifica que el CSV existe en S3 raw/"""
        return verify_file_in_s3(S3_KEY)

    @task()
    def register(s3_key: str) -> dict:
        """Registra la ingestión con metadata"""
        return log_ingestion(s3_key, DATASET_NAME)

    s3_key = verify()
    register(s3_key)


ingest_supply_chain()