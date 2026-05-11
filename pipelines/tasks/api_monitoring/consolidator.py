import logging
from datetime import datetime

def consolidar_resultados(reportes):
    log = logging.getLogger("airflow.task")
    log.info("Iniciando consolidación de resultados...")
    
    # Contar éxitos y fallos
    apis_exitosas = [r for r in reportes if r["exito"] is True]
    apis_fallidas = [r for r in reportes if r["exito"] is False]
    
    total_apis = len(reportes)
    total_exitosas = len(apis_exitosas)
    total_fallidas = len(apis_fallidas)
    
    # Calcular tiempo promedio de respuesta (solo de las que respondieron)
    tiempos = [r["tiempo_respuesta_segundos"] for r in reportes if r["tiempo_respuesta_segundos"] > 0]
    tiempo_promedio = round(sum(tiempos) / len(tiempos), 4) if tiempos else 0
    
    # Armar el reporte final consolidado
    reporte_final = {
        "fecha_ejecucion": datetime.now().isoformat(),
        "metricas": {
            "total_apis": total_apis,
            "exitosas": total_exitosas,
            "fallidas": total_fallidas,
            "tiempo_promedio_segundos": tiempo_promedio
        },
        "detalles_por_api": reportes
    }
    
    # Generar logs de métricas finales
    log.info(f"===== MÉTRICAS FINALES =====")
    log.info(f"Total APIs monitoreadas: {total_apis}")
    log.info(f"✅ Exitosas: {total_exitosas}")
    log.info(f"❌ Fallidas: {total_fallidas}")
    log.info(f"⏱️  Tiempo promedio de respuesta: {tiempo_promedio} segundos")
    log.info(f"===============================")
    
    return reporte_final