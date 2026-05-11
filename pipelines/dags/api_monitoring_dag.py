from airflow.decorators import dag, task
from datetime import datetime
import json
import logging

from tasks.api_monitoring.validator import validar_api
from tasks.api_monitoring.consolidator import consolidar_resultados
from airflow.models import Variable

@dag(
    dag_id="pipeline_monitoreo_apis",
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["monitoreo", "apis", "ejercicio_3"],
)
def monitoreo_apis_dag():

    @task(retries=2, retry_delay=30)
    def validar_users():
        return validar_api(
            connection_id="api_jsonplaceholder_users",
            endpoint="/users",
            expected_status_code=200,
            min_expected_records=1,
            expected_data_type="list",
            max_response_time_seconds=5.0
        )

    @task(retries=2, retry_delay=30)
    def validar_posts():
        return validar_api(
            connection_id="api_jsonplaceholder_posts",
            endpoint="/posts",
            expected_status_code=200,
            min_expected_records=1,
            expected_data_type="list",
            max_response_time_seconds=5.0
        )

    @task(retries=2, retry_delay=30)
    def validar_comments():
        return validar_api(
            connection_id="api_jsonplaceholder_comments",
            endpoint="/comments",
            expected_status_code=200,
            min_expected_records=1,
            expected_data_type="list",
            max_response_time_seconds=10.0
        )

    t_users = validar_users()
    t_posts = validar_posts()
    t_comments = validar_comments()

    @task
    def consolidar_y_guardar(repo_users, repo_posts, repo_comments):
        log = logging.getLogger("airflow.task")
        
        reportes = [repo_users, repo_posts, repo_comments]
        reporte_final = consolidar_resultados(reportes)
        
        reporte_json = json.dumps(reporte_final, indent=2, ensure_ascii=False)
        
        Variable.set("reporte_monitoreo_apis", reporte_json)
        log.info("✅ Reporte consolidado guardado en Variable: reporte_monitoreo_apis")
        
        return reporte_final

    t_consolidar = consolidar_y_guardar(t_users, t_posts, t_comments)

    [t_users, t_posts, t_comments] >> t_consolidar

# Esta línea registra el DAG en Airflow
dag_instance = monitoreo_apis_dag()