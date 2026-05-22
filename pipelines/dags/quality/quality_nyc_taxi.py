from airflow.sdk import dag, task
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import pyarrow.parquet as pq
import io
from datetime import datetime

from tasks.quality.clean_nyc import clean_nyc_nulls
from tasks.quality.validators import filter_positive_duration

S3_BUCKET = "scorpius-airflow-logs-2026"
S3_KEY_RAW = "raw/nyc_taxi/2024/01/yellow_tripdata_2024-01.parquet"
S3_KEY_CLEAN = "clean/nyc_taxi/yellow_tripdata_2024-01_clean.parquet"

@dag(
    dag_id="quality_nyc_taxi",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["quality", "nyc_taxi"],
)
def quality_nyc_taxi():

    @task
    def limpiar_y_guardar():
        hook = S3Hook(aws_conn_id="aws_default")
        
        # 1. Leer SOLO las 5 columnas necesarias con PyArrow (Evita el error OOM)
        obj = hook.get_key(key=S3_KEY_RAW, bucket_name=S3_BUCKET)
        table = pq.read_table(
            obj.get()["Body"].read(),
            columns=["tpep_pickup_datetime", "tpep_dropoff_datetime", "passenger_count", "trip_distance", "total_amount"]
        )
        
        # 2. Convertir a Pandas (ahora es muy ligero, no llena la RAM)
        df = table.to_pandas()
        
        # 3. Limpiar datos (funciones del M3)
        df = clean_nyc_nulls(df)
        df = filter_positive_duration(df, "tpep_pickup_datetime", "tpep_dropoff_datetime")
        
        # 4. Guardar en S3
        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False)
        
        hook.load_file_obj(
            file_obj=buffer,
            key=S3_KEY_CLEAN,
            bucket_name=S3_BUCKET,
            replace=True
        )
        print("Guardado exitosamente en S3: clean/nyc_taxi/")

    limpiar_y_guardar()

quality_nyc_taxi()
