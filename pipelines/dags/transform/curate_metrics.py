from airflow.sdk import dag, task
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import pyarrow.parquet as pq
import io
from datetime import datetime

from tasks.metrics.calculate_kpis import calcular_kpis_nyc, calcular_kpis_amazon

S3_BUCKET = "scorpius-airflow-logs-2026"

@dag(
    dag_id="curate_metrics",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["transform", "curated"],
)
def curate_metrics():

    @task
    def procesar_nyc():
        hook = S3Hook(aws_conn_id="aws_default")

        obj = hook.get_key(key="clean/nyc_taxi/yellow_tripdata_2024-01_clean.parquet", bucket_name=S3_BUCKET)
        data = obj.get()["Body"].read()
        # ✅ PyArrow en lugar de pandas directo — evita OOM en t3.small
        df = pq.read_table(io.BytesIO(data)).to_pandas()

        df_kpis = calcular_kpis_nyc(df)

        buffer = io.BytesIO()
        df_kpis.to_parquet(buffer, index=False)
        buffer.seek(0)

        hook.load_file_obj(
            file_obj=buffer,
            key="curated/kpis_nyc.parquet",
            bucket_name=S3_BUCKET,
            replace=True
        )
        print("KPIs de NYC guardados en curated/")

    @task
    def procesar_amazon():
        hook = S3Hook(aws_conn_id="aws_default")

        obj = hook.get_key(key="clean/amazon_delivery/amazon_delivery_clean.parquet", bucket_name=S3_BUCKET)
        data = obj.get()["Body"].read()
        # ✅ PyArrow en lugar de pandas directo
        df = pq.read_table(io.BytesIO(data)).to_pandas()

        print("¡ATENCION! Estas son las columnas del archivo de Amazon:", df.columns.tolist())

        df_kpis = calcular_kpis_amazon(df)

        buffer = io.BytesIO()
        df_kpis.to_parquet(buffer, index=False)
        buffer.seek(0)

        hook.load_file_obj(
            file_obj=buffer,
            key="curated/kpis_amazon.parquet",
            bucket_name=S3_BUCKET,
            replace=True
        )
        print("KPIs de Amazon guardados en curated/")

    procesar_nyc()
    procesar_amazon()

curate_metrics()