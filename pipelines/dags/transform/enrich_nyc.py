from airflow.sdk import dag, task
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import pyarrow.parquet as pq
import io
from datetime import datetime

from tasks.metrics.feature_engineering import agregar_trip_duration, agregar_z_score_duracion

S3_BUCKET = "scorpius-airflow-logs-2026"
S3_KEY_INPUT = "clean/nyc_taxi/yellow_tripdata_2024-01_clean.parquet"
S3_KEY_OUTPUT = "curated/nyc_enriched.parquet"

@dag(
    dag_id="enrich_nyc_taxi",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["transform", "nyc_taxi"],
)
def enrich_nyc_taxi():

    @task
    def enriquecer_y_guardar():
        hook = S3Hook(aws_conn_id="aws_default")

        # 1. Leer desde clean/
        response = hook.get_key(key=S3_KEY_INPUT, bucket_name=S3_BUCKET).get()
        buffer = io.BytesIO(response["Body"].read())
        table = pq.read_table(buffer)
        buffer.close()
        df = table.to_pandas()

        filas_originales = len(df)
        print(f"Filas leídas desde clean/: {filas_originales}")

        # 2. Aplicar funciones de M3 en orden
        df = agregar_trip_duration(df)
        df = agregar_z_score_duracion(df)

        # 3. Verificar que no se perdieron filas
        print(f"Filas después del enriquecimiento: {len(df)}")

        # 4. Guardar en curated/
        output_buffer = io.BytesIO()
        df.to_parquet(output_buffer, index=False)
        output_buffer.seek(0)

        hook.load_file_obj(
            file_obj=output_buffer,
            key=S3_KEY_OUTPUT,
            bucket_name=S3_BUCKET,
            replace=True
        )
        print(f"Guardado en S3: curated/nyc_enriched.parquet — {len(df)} filas, {len(df.columns)} columnas")

    enriquecer_y_guardar()

enrich_nyc_taxi()