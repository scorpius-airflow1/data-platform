from datetime import datetime
from airflow.sdk import dag, task
from tasks.ingest.download_kaggle import verify_file_in_s3, log_ingestion

S3_KEY = "raw/amazon_delivery/amazon_delivery.csv"
DATASET_NAME = "amazon_delivery"


@dag(
    dag_id="ingest_amazon_delivery",
    description="Verifica y registra ingestión de Amazon Delivery Dataset en S3 raw/",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["ingesta", "amazon_delivery", "raw"],
    default_args={"queue": "default"},
)
def ingest_amazon_delivery():

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


ingest_amazon_delivery()