from airflow.decorators import dag
from datetime import datetime
from tasks.hello_task import get_server_info


@dag(
    dag_id="example_hello_world",
    schedule=None,
    queue="test",
    catchup=False,
    tags=["example"],
)
def example_dag():

    get_server_info()

dag_instance = example_dag()