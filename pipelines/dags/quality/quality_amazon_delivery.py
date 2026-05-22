from airflow.sdk import dag, task
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import pandas as pd
import io
from datetime import datetime

from tasks.quality.clean_amazon import clean_amazon_nulls
from tasks.quality.validators import filter_gps_valid

S3_BUCKET = "scorpius-airflow-logs-2026"
S3_KEY = "raw/amazon_delivery/amazon_delivery.csv"

@dag(
    dag_id="quality_amazon_delivery",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["quality", "amazon_delivery"],
)
def quality_amazon_delivery():

    @task
    def limpiar_y_guardar():
        hook = S3Hook(aws_conn_id="aws_default")
        obj = hook.get_key(key=S3_KEY, bucket_name=S3_BUCKET)
        data = obj.get()["Body"].read()
        
        df = pd.read_csv(io.BytesIO(data))
        df = clean_amazon_nulls(df)
        df = filter_gps_valid(df, "Store_Latitude", "Store_Longitude")
        df = filter_gps_valid(df, "Drop_Latitude", "Drop_Longitude")
        
        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False)
        hook.load_bytes(
            bytes_data=buffer.getvalue(),
            key="clean/amazon_delivery/amazon_delivery_clean.parquet",
            bucket_name=S3_BUCKET,
            replace=True
        )
        print("Guardado en S3: clean/amazon_delivery/")

    limpiar_y_guardar()

quality_amazon_delivery()