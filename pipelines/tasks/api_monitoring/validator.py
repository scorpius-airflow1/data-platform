import json
import time
import logging

from airflow.hooks.base import BaseHook

def validar_api(
    connection_id,
    endpoint,
    expected_status_code=200,
    min_expected_records=1,
    expected_data_type="list",
    max_response_time_seconds=5.0
):