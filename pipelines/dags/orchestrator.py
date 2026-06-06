from airflow.sdk import dag, task
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime

@dag(
    dag_id="master_orchestrator",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",  # Se ejecuta automáticamente todos los días
    catchup=False,
    tags=["orchestrator", "master"],
    doc_md="""DAG Maestro que orquesta todo el pipeline de Scorpius de forma automática."""
)
def master_orchestrator():

    # FASE 1: INGESTA
    ingest_amazon = TriggerDagRunOperator(
        task_id="trigger_ingest_amazon",
        trigger_dag_id="ingest_amazon_delivery",
        wait_for_completion=True,
        poke_interval=30
    )

    ingest_nyc = TriggerDagRunOperator(
        task_id="trigger_ingest_nyc",
        trigger_dag_id="ingest_nyc_taxi",
        wait_for_completion=True,
        poke_interval=30
    )

    # FASE 2: CALIDAD (Depende de que la ingesta termine)
    quality_amazon = TriggerDagRunOperator(
        task_id="trigger_quality_amazon",
        trigger_dag_id="quality_amazon_delivery",
        wait_for_completion=True,
        poke_interval=30
    )

    quality_nyc = TriggerDagRunOperator(
        task_id="trigger_quality_nyc",
        trigger_dag_id="quality_nyc_taxi",
        wait_for_completion=True,
        poke_interval=30
    )

    # FASE 3: CURACION (Depende de que la calidad termine)
    curate_metrics = TriggerDagRunOperator(
        task_id="trigger_curate_metrics",
        trigger_dag_id="curate_metrics",
        wait_for_completion=True,
        poke_interval=30
    )

    # ORQUESTACIÓN: El flujo exacto
    [ingest_amazon, ingest_nyc] >> [quality_amazon, quality_nyc] >> curate_metrics

master_orchestrator()