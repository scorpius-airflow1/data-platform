from airflow.sdk import dag, task
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import pandas as pd
import io
from datetime import datetime

S3_BUCKET = "scorpius-airflow-logs-2026"
# Apuntamos a la carpeta (prefijo) en lugar de a un archivo fijo
S3_FOLDER_INPUT = "clean/amazon_delivery/"
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

        # 1. Listar los archivos dentro de la carpeta de S3
        print(f"Buscando archivos en: s3://{S3_BUCKET}/{S3_FOLDER_INPUT}")
        all_keys = hook.list_keys(bucket_name=S3_BUCKET, prefix=S3_FOLDER_INPUT)
        
        # Filtrar para evitar carpetas vacías o archivos ocultos, nos quedamos con los .parquet
        valid_files = [k for k in all_keys if k.endswith('.parquet')]
        
        if not valid_files:
            raise FileNotFoundError(f"No se encontraron archivos Parquet en s3://{S3_BUCKET}/{S3_FOLDER_INPUT}")
        
        # Tomamos el primer archivo encontrado (que es donde dejó los datos clean_amazon.py)
        archivo_a_leer = valid_files[0]
        print(f"Leyendo archivo encontrado: {archivo_a_leer}")

        # 2. Leer los bytes del archivo y cargarlo a Pandas
        file_content = hook.read_key(key=archivo_a_leer, bucket_name=S3_BUCKET)
        # Validamos si viene como string o bytes para evitar errores de codificación
        bytes_data = file_content.encode('utf-8') if isinstance(file_content, str) else file_content
        df = pd.read_parquet(io.BytesIO(bytes_data))

        filas_originales = len(df)
        print(f"Filas leídas correctamente: {filas_originales}")

        # 3. Categorizar Delivery_Time
        def categorizar_entrega(minutos):
            if minutos < 90:
                return "Rápido"
            elif minutos <= 160:
                return "Normal"
            else:
                return "Crítico"

        df['categoria_entrega'] = df['Delivery_Time'].apply(categorizar_entrega)

        print(f"Distribución de categorías:")
        print(df['categoria_entrega'].value_counts())

        # 4. Verificar que no se perdieron filas
        assert len(df) == filas_originales, "ERROR: se perdieron filas"

        # 5. Guardar el resultado en la capa Curated (como un archivo consolidado)
        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False)
        buffer.seek(0)

        hook.load_file_obj(
            file_obj=buffer,
            key=S3_KEY_OUTPUT,
            bucket_name=S3_BUCKET,
            replace=True
        )
        print(f"¡Éxito! Guardado en S3: {S3_KEY_OUTPUT} — {len(df)} filas.")

    enriquecer_y_guardar()

enrich_amazon_delivery()