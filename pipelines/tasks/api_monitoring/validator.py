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
    # Inicializar logger para esta tarea
    log = logging.getLogger("airflow.task")
    
    # Obtener la conexión desde Airflow
    log.info(f"Obteniendo conexión: {connection_id}")
    conn = BaseHook.get_connection(connection_id)
    
    # Armar la URL completa
    url = f"{conn.schema}://{conn.host}{endpoint}"
    log.info(f"URL construida: {url}")
    
    # Iniciar cronómetro
    start_time = time.time()

    resultado = {
        "api": endpoint,
        "url": url,
        "exito": False,
        "status_code": None,
        "cantidad_registros": 0,
        "tiempo_respuesta_segundos": 0,
        "validacion_estructura": False,
        "error": None
    }

    try:
        import requests
        
        log.info(f"Haciendo petición GET a {url}")
        response = requests.get(url, timeout=max_response_time_seconds)
        
        tiempo_total = time.time() - start_time
        resultado["tiempo_respuesta_segundos"] = round(tiempo_total, 4)
        log.info(f"Respuesta recibida en {resultado['tiempo_respuesta_segundos']} segundos")

        # 1. Validar Status Code
        log.info(f"Status code recibido: {response.status_code}")
        resultado["status_code"] = response.status_code
        
        if response.status_code != expected_status_code:
            raise ValueError(f"Status code incorrecto. Se esperaba {expected_status_code} y se recibió {response.status_code}")

        # 2. Parsear la respuesta a JSON
        log.info("Parseando respuesta a JSON...")
        data = response.json()

        # 3. Validar estructura (tipo de dato)
        log.info(f"Tipo de dato recibido: {type(data).__name__}")
        if expected_data_type == "list":
            if not isinstance(data, list):
                raise TypeError(f"Se esperaba una lista pero se recibió {type(data).__name__}")
            resultado["validacion_estructura"] = True
            
            # 4. Validar cantidad de registros
            resultado["cantidad_registros"] = len(data)
            log.info(f"Cantidad de registros: {resultado['cantidad_registros']}")

            if len(data) < min_expected_records:
                raise ValueError(f"Registros insuficientes. Se esperaban al menos {min_expected_records} y se recibieron {len(data)}")
        else:
            resultado["validacion_estructura"] = True

        # Si llegó hasta aquí, ¡todo pasó!
        resultado["exito"] = True
        log.info(f"✅ API {endpoint} validada exitosamente")

    except Exception as e:
        # Calcular tiempo aunque haya fallado
        tiempo_total = time.time() - start_time
        resultado["tiempo_respuesta_segundos"] = round(tiempo_total, 4)
        
        # Guardar el mensaje de error en el reporte
        error_msg = f"{type(e).__name__}: {str(e)}"
        resultado["error"] = error_msg
        
        # Registrar el error en los logs
        log.error(f"❌ Error validando {endpoint}: {error_msg}")

    # Retornar el reporte final (se ejecuta pase lo que pase)
    return resultado