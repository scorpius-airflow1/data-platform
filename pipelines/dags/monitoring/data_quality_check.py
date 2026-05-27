# pipelines/dags/monitoring/data_quality_check.py

from airflow.decorators import dag, task
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from datetime import datetime
import pandas as pd
import io


@dag(
    dag_id='data_quality_check',
    description='Centinela de calidad: verifica que curated/nyc_enriched.parquet no tenga nulos en z_score_duracion',
    schedule_interval=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['monitoring', 'quality', 'scorpius']
)
def data_quality_check():

    @task()
    def leer_datos_enriquecidos():
        """Lee curated/nyc_enriched.parquet desde S3."""
        hook = S3Hook(aws_conn_id='aws_default')

        s3_key = 'curated/nyc_enriched.parquet'
        bucket = 'scorpius-airflow-logs-2026'

        print(f"Leyendo s3://{bucket}/{s3_key}...")

        objeto = hook.get_key(key=s3_key, bucket_name=bucket)
        contenido = objeto.get()['Body'].read()

        df = pd.read_parquet(io.BytesIO(contenido))

        print(f"Archivo leído correctamente: {len(df)} filas, columnas: {list(df.columns)}")

        return df.to_json()

    @task()
    def verificar_calidad(df_json: str):
        """Verifica que z_score_duracion no tenga valores nulos."""
        import json
        df = pd.read_json(df_json)

        columna = 'z_score_duracion'

        # Verificar que la columna existe
        if columna not in df.columns:
            raise ValueError(
                f"La columna '{columna}' no existe en el archivo. "
                f"Columnas disponibles: {list(df.columns)}"
            )

        # Verificar nulos
        nulos = df[columna].isnull().sum()

        if nulos > 0:
            raise ValueError(
                f"Datos nulos encontrados: la columna '{columna}' "
                f"tiene {nulos} valores nulos de {len(df)} filas totales."
            )

        # Verificar que los valores son numéricos y razonables
        if df[columna].min() < 0:
            raise ValueError(
                f"Z-scores negativos detectados en '{columna}'. "
                f"Revisar la lógica de feature_engineering.py."
            )

        print(f"Calidad OK — '{columna}' sin nulos en {len(df)} filas.")
        print(f"Z-score máximo: {df[columna].max():.2f}")
        print(f"Rutas atípicas (z > 3): {(df[columna] > 3).sum()}")

    # Definir el flujo
    datos = leer_datos_enriquecidos()
    verificar_calidad(datos)


data_quality_check()