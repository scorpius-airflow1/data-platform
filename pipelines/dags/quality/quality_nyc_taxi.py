from airflow.sdk import dag, task
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import pandas as pd
import io
from datetime import datetime

from tasks.quality.clean_nyc import clean_nyc_nulls
from tasks.quality.validators import filter_gps_valid, filter_positive_duration

@dag(
    dag_id="quality_nyc_taxi",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["quality", "nyc_taxi"],
)
def quality_nyc_taxi():

    @task
    def leer_desde_s3() -> bytes:
        hook = S3Hook(aws_conn_id="aws_default")
        obj = hook.get_key(
            key="raw/nyc_taxi/2024/01/yellow_tripdata_2024-01.parquet",
            bucket_name="scorpius-airflow-logs-2026"
        )
        return obj.get()["Body"].read()

    @task
    def limpiar(data: bytes) -> bytes:
        df = pd.read_parquet(io.BytesIO(data))
        df = clean_nyc_nulls(df)
        df = filter_positive_duration(df, "tpep_pickup_datetime", "tpep_dropoff_datetime")
        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False)
        return buffer.getvalue()

    @task
    def guardar_en_s3(data: bytes):
        hook = S3Hook(aws_conn_id="aws_default")
        hook.load_bytes(
            bytes_data=data,
            key="clean/nyc_taxi/yellow_tripdata_2024-01_clean.parquet",
            bucket_name="scorpius-airflow-logs-2026",
            replace=True
        )
        print("Guardado en S3: clean/nyc_taxi/")

    raw = leer_desde_s3()
    limpio = limpiar(raw)
    guardar_en_s3(limpio)

quality_nyc_taxi()