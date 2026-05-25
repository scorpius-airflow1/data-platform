from airflow.sdk import dag, task
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import pandas as pd
import io
from datetime import datetime

S3_BUCKET = "scorpius-airflow-logs-2026"
S3_KEY = "raw/supply_chain/supply_chain_data.csv"

@dag(
    dag_id="quality_supply_chain",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["quality", "supply_chain"],
)
def quality_supply_chain():

    @task
    def limpiar_y_guardar():
        hook = S3Hook(aws_conn_id="aws_default")

        # 1. Descargar
        obj = hook.get_key(key=S3_KEY, bucket_name=S3_BUCKET)
        data = obj.get()["Body"].read()

        # 2. Leer — sin limpieza porque no tiene nulos ni duplicados
        df = pd.read_csv(io.BytesIO(data))
        print(f" - Supply Chain cargado: {len(df)} filas, {len(df.columns)} columnas")

        # 3. Guardar en Parquet
        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False)
        hook.load_bytes(
            bytes_data=buffer.getvalue(),
            key="clean/supply_chain/supply_chain_data_clean.parquet",
            bucket_name=S3_BUCKET,
            replace=True
        )
        print("Guardado en S3: clean/supply_chain/")

    limpiar_y_guardar()

quality_supply_chain()