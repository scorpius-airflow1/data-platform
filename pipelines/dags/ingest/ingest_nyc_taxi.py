from datetime import datetime
from airflow.decorators import dag, task
from tasks.ingest.download_nyc import download_nyc_taxi, upload_to_s3, cleanup_local

YEAR = 2024
MONTH = 1


@dag(
    dag_id="ingest_nyc_taxi",
    description="Descarga NYC Taxi Jan 2024 y lo sube a S3 raw/",
    start_date=datetime(2024, 1, 1),
    schedule=None,          # manual por ahora, Semana 1
    catchup=False,
    tags=["ingesta", "nyc_taxi", "raw"],
)
def ingest_nyc_taxi():

    @task()
    def download(year: int, month: int) -> str:
        """Descarga el parquet de NYC Taxi a /tmp"""
        return download_nyc_taxi(year=year, month=month)

    @task()
    def upload(local_path: str, year: int, month: int) -> str:
        """Sube el parquet a S3 raw/nyc_taxi/YYYY/MM/"""
        return upload_to_s3(local_path=local_path, year=year, month=month)

    @task()
    def cleanup(local_path: str) -> None:
        """Elimina el archivo temporal del worker"""
        cleanup_local(local_path)

    # Orquestación: download → upload → cleanup
    local_file = download(YEAR, MONTH)
    s3_key = upload(local_file, YEAR, MONTH)
    cleanup(local_file)


ingest_nyc_taxi()