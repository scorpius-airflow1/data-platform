from airflow.sdk import dag, task
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import pandas as pd
import io
from datetime import datetime

S3_BUCKET = "scorpius-airflow-logs-2026"
S3_KEY_INPUT = "clean/amazon_delivery/amazon_delivery_clean.parquet"
S3_KEY_OUTPUT = "curated/amazon_enriched.parquet"

@dag(
    dag_id="enrich_amazon_delivery",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["transform", "amazon_delivery"],
)
def enrich_amazon_delivery():

    @task
    def enriquecer_y_guardar():
        hook = S3Hook(aws_conn_id="aws_default")

        # 1. Leer desde clean/ correctamente como bytes
        response = hook.get_key(key=S3_KEY_INPUT, bucket_name=S3_BUCKET).get()
        df = pd.read_parquet(io.BytesIO(response["Body"].read()))

        filas_originales = len(df)
        print(f"Filas leídas desde clean/: {filas_originales}")

        # 2. Categorizar Delivery_Time
        def categorizar_entrega(minutos):
            if minutos < 90:
                return "Rápido"
            elif minutos <= 160:
                return "Normal"
            else:
                return "Crítico"

        df['categoria_entrega'] = df['Delivery_Time'].apply(categorizar_entrega)

        print(f"Distribución de categorías:")
        print(df['categoria_entrega'].value_counts().to_string())

        # 3. Verificar que no se perdieron filas
        assert len(df) == filas_originales, "ERROR: se perdieron filas"

        # 4. Guardar en curated/
        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False)
        buffer.seek(0)

        hook.load_file_obj(
            file_obj=buffer,
            key=S3_KEY_OUTPUT,
            bucket_name=S3_BUCKET,
            replace=True
        )
        print(f"Guardado en S3: curated/amazon_enriched.parquet — {len(df)} filas, {len(df.columns)} columnas")

    enriquecer_y_guardar()

enrich_amazon_delivery()