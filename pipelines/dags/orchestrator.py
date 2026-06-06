from airflow.sdk import dag
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime

@dag(
    dag_id="master_orchestrator",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["orchestrator", "master"],
)
def master_orchestrator():

    # FASE 1: INGESTA
    ingest_amazon = TriggerDagRunOperator(
        task_id="trigger_ingest_amazon",
        trigger_dag_id="ingest_amazon_delivery",
    )

    ingest_nyc = TriggerDagRunOperator(
        task_id="trigger_ingest_nyc",
        trigger_dag_id="ingest_nyc_taxi",
    )

    # FASE 2: CALIDAD
    quality_amazon = TriggerDagRunOperator(
        task_id="trigger_quality_amazon",
        trigger_dag_id="quality_amazon_delivery",
    )

    quality_nyc = TriggerDagRunOperator(
        task_id="trigger_quality_nyc",
        trigger_dag_id="quality_nyc_taxi",
    )

    # FASE 3: CURACION
    curate_metrics = TriggerDagRunOperator(
        task_id="trigger_curate_metrics",
        trigger_dag_id="curate_metrics",
    )

    # ORQUESTACIÓN (Lineal para evitar el TypeError de listas en Airflow 3.x)
    ingest_amazon >> quality_amazon >> curate_metrics
    ingest_nyc >> quality_nyc >> curate_metrics

master_orchestrator()