from airflow.sdk import dag, task
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import pandas as pd
import io
from datetime import datetime

# Importamos las funciones que acaba de crear M3
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
        
        # 1. Leer datos limpios
        obj = hook.get_key(key="clean/nyc_taxi/yellow_tripdata_2024-01_clean.parquet", bucket_name=S3_BUCKET)
        data = obj.get()["Body"].read()
        df = pd.read_parquet(io.BytesIO(data))
        
        # 2. Aplicar lógica de M3
        df_kpis = calcular_kpis_nyc(df)
        
        # 3. Guardar en curated/
        buffer = io.BytesIO()
        df_kpis.to_parquet(buffer, index=False)
        buffer.seek(0) # ¡CLAVE! Sin esto, el archivo pesa 0 bytes.
        
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
        
        # 1. Leer datos limpios
        obj = hook.get_key(key="clean/amazon_delivery/amazon_delivery_clean.parquet", bucket_name=S3_BUCKET)
        data = obj.get()["Body"].read()
        df = pd.read_parquet(io.BytesIO(data))

         # --- TRAMPA DE DEBUGGING INICIO ---
        print("¡ATENCION! Estas son las columnas del archivo de Amazon:", df.columns.tolist())
        # --- TRAMPA DE DEBUGGING FIN ---
        
        # 2. Aplicar lógica de M3
        df_kpis = calcular_kpis_amazon(df)
        
        # 3. Guardar en curated/
        buffer = io.BytesIO()
        df_kpis.to_parquet(buffer, index=False)
        buffer.seek(0) # ¡CLAVE!
        
        hook.load_file_obj(
            file_obj=buffer,
            key="curated/kpis_amazon.parquet",
            bucket_name=S3_BUCKET,
            replace=True
        )
        print("KPIs de Amazon guardados en curated/")

    # Ejecutar ambas tareas
    procesar_nyc()
    procesar_amazon()

curate_metrics()