from datetime import datetime
from airflow.sdk import dag, task
from tasks.ingest.download_nyc import download_nyc_taxi, upload_to_s3, cleanup_local

YEAR = 2024
MONTH = 1

@dag(
    dag_id="ingest_nyc_taxi",
    description="Descarga NYC Taxi Jan 2024 y lo sube a S3 raw/",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["ingesta", "nyc_taxi", "raw"],
)
def ingest_nyc_taxi():

    @task()
    def ingest_nyc_pipeline(year: int, month: int):
        """Descarga, sube a S3 y limpia en el mismo Worker para evitar FileNotFoundError"""
        local_path = download_nyc_taxi(year=year, month=month)
        upload_to_s3(local_path=local_path, year=year, month=month)
        cleanup_local(local_path)

    ingest_nyc_pipeline(YEAR, MONTH)

ingest_nyc_taxi()