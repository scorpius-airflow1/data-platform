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
        df = pq.read_table(io.BytesIO(data)).to_pandas()

        # Ahora devuelve un DataFrame agrupado por hora
        df_kpis = calcular_kpis_nyc(df)

        buffer = io.BytesIO()
        df_kpis.to_parquet(buffer, index=False)
        buffer.seek(0) # Regla de oro de Scorpius

        hook.load_file_obj(
            file_obj=buffer,
            key="curated/nyc_vista_hora.parquet", # Nombre exacto para M4
            bucket_name=S3_BUCKET,
            replace=True
        )
        print("KPIs de NYC por hora guardados en curated/")

    @task
    def procesar_amazon():
        hook = S3Hook(aws_conn_id="aws_default")
        
        obj = hook.get_key(key="clean/amazon_delivery/amazon_delivery_clean.parquet", bucket_name=S3_BUCKET)
        data = obj.get()["Body"].read()
        df = pq.read_table(io.BytesIO(data)).to_pandas()

        # Ahora devuelve un DICCIONARIO con dos DataFrames
        kpis_dict = calcular_kpis_amazon(df)

        # 1. Guardar Vista por Zona
        buffer_zona = io.BytesIO()
        kpis_dict["vista_zona"].to_parquet(buffer_zona, index=False)
        buffer_zona.seek(0) # Regla de oro
        
        hook.load_file_obj(
            file_obj=buffer_zona,
            key="curated/amazon_vista_zona.parquet",
            bucket_name=S3_BUCKET,
            replace=True
        )
        print("Vista por zona de Amazon guardada en curated/")

        # 2. Guardar Vista por Vehículo
        buffer_vehiculo = io.BytesIO()
        kpis_dict["vista_vehiculo"].to_parquet(buffer_vehiculo, index=False)
        buffer_vehiculo.seek(0) # Regla de oro
        
        hook.load_file_obj(
            file_obj=buffer_vehiculo,
            key="curated/amazon_vista_vehiculo.parquet",
            bucket_name=S3_BUCKET,
            replace=True
        )
        print("Vista por vehículo de Amazon guardada en curated/")

    # Secuencia obligatoria para evitar OOM (Out of Memory)
    nyc = procesar_nyc()
    amazon = procesar_amazon()
    
    nyc >> amazon

curate_metrics()