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
        
        # 1. Descargar directamente en un buffer de memoria seguro para PyArrow
        response = hook.get_key(key=S3_KEY_RAW, bucket_name=S3_BUCKET).get()
        buffer = io.BytesIO(response["Body"].read())
        
        # 2. Leer SOLO las 5 columnas necesarias desde el buffer
        table = pq.read_table(
            buffer,
            columns=["tpep_pickup_datetime", "tpep_dropoff_datetime", "passenger_count", "trip_distance", "total_amount"]
        )
        
        # Cerramos el buffer para liberar la memoria de los 47MB crudos
        buffer.close()
        
        # 3. Convertir a Pandas (muy ligero)
        df = table.to_pandas()
        
        # 4. Limpiar datos (funciones del M3)
        df = clean_nyc_nulls(df)
        df = filter_positive_duration(df, "tpep_pickup_datetime", "tpep_dropoff_datetime")
        
        # 5. Guardar en S3
        output_buffer = io.BytesIO()
        df.to_parquet(output_buffer, index=False)
        
        hook.load_file_obj(
            file_obj=output_buffer,
            key=S3_KEY_CLEAN,
            bucket_name=S3_BUCKET,
            replace=True
        )
        print("Guardado exitosamente en S3: clean/nyc_taxi/")

    limpiar_y_guardar()

quality_nyc_taxi()