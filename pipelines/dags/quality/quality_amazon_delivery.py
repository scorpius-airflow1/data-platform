from airflow.sdk import dag, task
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import pandas as pd
import io
from datetime import datetime

from tasks.quality.clean_amazon import clean_amazon_nulls
from tasks.quality.validators import filter_gps_valid

@dag(
    dag_id="quality_amazon_delivery",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["quality", "amazon_delivery"],
)
def quality_amazon_delivery():

    @task
    def leer_desde_s3() -> bytes:
        hook = S3Hook(aws_conn_id="aws_s3_logs_2026")
        obj = hook.get_key(
            key="raw/amazon_delivery/amazon_delivery.csv",
            bucket_name="scorpius-airflow-logs-2026"
        )
        return obj.get()["Body"].read()

    @task
    def limpiar(data: bytes) -> bytes:
        df = pd.read_csv(io.BytesIO(data))
        df = clean_amazon_nulls(df)
        df = filter_gps_valid(df, "Store_Latitude", "Store_Longitude")
        df = filter_gps_valid(df, "Drop_Latitude", "Drop_Longitude")
        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False)
        return buffer.getvalue()

    @task
    def guardar_en_s3(data: bytes):
        hook = S3Hook(aws_conn_id="aws_default")
        hook.load_bytes(
            bytes_data=data,
            key="clean/amazon_delivery/amazon_delivery_clean.parquet",
            bucket_name="scorpius-airflow-logs-2026",
            replace=True
        )
        print("Guardado en S3: clean/amazon_delivery/")

    raw = leer_desde_s3()
    limpio = limpiar(raw)
    guardar_en_s3(limpio)

quality_amazon_delivery()