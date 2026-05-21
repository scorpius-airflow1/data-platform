# INFORME DE DISEÑO DE KPIS, GESTIÓN DE ANOMALÍAS Y ESTRATEGIA DE REPORTES

**Proyecto:** Solución Analítica para el Colapso Logístico y de Distribución

**Fecha de Emisión:** 2026-05-21

**Estado:** Propuesta Técnica Lista para Implementación

## 1. ALINEACIÓN ESTRATÉGICA Y ADAPTACIÓN AL NEGOCIO

Ante la problemática actual de retrasos, pérdida de mercancía, inconsistencias en inventarios y métricas contradictorias entre las áreas operativa y financiera, se rediseñó la matriz de indicadores.

Los KPIs propuestos no solo miden los tiempos de traslado, sino que introducen auditorías de calidad de datos (duplicados) y conciliaciones de negocio (inventario y costos de ineficiencia) utilizando como base los datasets de NYC Taxi Trip Records, Amazon Delivery y Supply Chain.

## 2. MATRIZ DE INDICADORES CLAVE DE RENDIMIENTO (KPIS)

### [RENDIMIENTO DE RUTAS]

**KPI 1: Tiempo Promedio de Ruta**
- Fórmula: AVG(dropoff_time - pickup_time)
- Columnas Fuente: pickup_time, dropoff_time
- Frecuencia Sugerida: Cada hora / Diario

**KPI 2: Desviación Estándar del Tiempo de Viaje**
- Fórmula: STDDEV(dropoff_time - pickup_time)
- Columnas Fuente: pickup_time, dropoff_time
- Frecuencia Sugerida: Diario

### [EFICIENCIA OPERACIONAL]

**KPI 3: Tasa de Entregas Completadas**
- Fórmula: (COUNT(delivery_id) WHERE delivery_status = 'Completado' / COUNT(delivery_id)) * 100
- Columnas Fuente: delivery_status, delivery_id
- Frecuencia Sugerida: Diario

**KPI 4: Tasa de Entregas Fallidas y Devoluciones**
- Fórmula: (COUNT(delivery_id) WHERE delivery_status = 'Fallido' / COUNT(delivery_id)) * 100
- Columnas Fuente: delivery_status, delivery_id
- Frecuencia Sugerida: Diario

### [CONTROL FINANCIERO Y DE INVENTARIOS]

**KPI 5: Costo de Ineficiencia por Desviación Logística**
- Fórmula: SUM(operational_cost) WHERE z_score_distance > 3
- Columnas Fuente: trip_distance, operational_cost
- Frecuencia Sugerida: Diario
- Objetivo: Resolver las contradicciones entre las métricas operativas y financieras.

**KPI 6: Tasa de Discrepancia de Inventario**
- Fórmula: (ABS(SUM(physical_inventory_qty) - SUM(digital_inventory_qty)) / SUM(digital_inventory_qty)) * 100
- Columnas Fuente: physical_inventory_qty, digital_inventory_qty
- Frecuencia Sugerida: Diario
- Objetivo: Identificar la pérdida de mercancía y diferencias entre inventarios físicos y digitales.

### [ANOMALÍAS Y CALIDAD DE DATOS]

**KPI 7: Rutas Atípicas por Tiempo (Identificación de Cuellos de Botella)**
- Fórmula: COUNT(trip_id) WHERE z_score_time > 3
- Columnas Fuente: trip_duration, trip_id
- Frecuencia Sugerida: Cada hora / Diario

**KPI 8: Porcentaje de Registros Duplicados o Corruptos**
- Fórmula: ((COUNT(trip_id) - COUNT(DISTINCT trip_id)) / COUNT(trip_id)) * 100
- Columnas Fuente: trip_id
- Frecuencia Sugerida: Diario
- Objetivo: Mitigar el impacto de la información heterogénea y retrasada de operadores externos.

### [GEOGRÁFICOS]

**KPI 9: Zonas Críticas con Mayor Retraso Acumulado**
- Fórmula: SUM(delivery_delay) GROUP BY zone_id ORDER BY DESC
- Columnas Fuente: zone_id, delivery_delay
- Frecuencia Sugerida: Cada hora / Diario

**KPI 10: Tasa de Incidencias por Centro de Distribución (CD)**
- Fórmula: COUNT(incident_id) GROUP BY distribution_center_id
- Columnas Fuente: distribution_center_id, incident_id
- Frecuencia Sugerida: Diario

## 3. ESTRATEGIA DE NOTIFICACIÓN Y ACCESO AL DASHBOARD (TRIGGER EMAIL)

Para garantizar la máxima entregabilidad y compatibilidad con los gestores de correos corporativos (evitando bloqueos de scripts o mapas interactivos no soportados en HTML nativo), el reporte automatizado por correo se transforma en un "Disparador de Acción" directo hacia Power BI.

### Estructura de la Notificación Automatizada:

**Asunto:** [ALERTA LOGÍSTICA] Reporte Operacional de Distribución - [Fecha_Actual]

Estimado Equipo Directivo y de Operaciones,

Se ha generado el reporte de conciliación logística correspondiente al ciclo de procesamiento de datos actual. A continuación, se presenta el resumen ejecutivo con las alertas críticas del estado de la red de distribución:

**[ RESUMEN OPERACIONAL ]**
- Total de Viajes Procesados: [Valor_Dinámico]
- Tasa de Entregas Completadas: [Valor_Dinámico]%
- Alertas Activas en Centros de Distribución: [Cantidad]

**[ ALERTAS CRÍTICAS DE ANOMALÍAS ]**
- Se han detectado [X] rutas con desviaciones de tiempo atípicas (Z-Score > 3).
- La discrepancia actual entre el inventario físico en bodegas y el sistema digital se ubica en un [X]%.

**[ ACCESO AL DASHBOARD INTERACTIVO ]**
Para analizar el comportamiento geográfico detallado mediante mapas de calor, aislar los problemas por operador logístico, evaluar el impacto financiero de las devoluciones y auditar las rutas ineficientes, acceda al reporte oficial:

VER DASHBOARD COMPLETO EN POWER BI
(https://app.powerbi.com/groups/me/reports/logistics_distribution_analytics)

Nota de TI: Este correo ha sido automatizado por el pipeline de Ingeniería de Datos. Última actualización del Data Lakehouse: [Timestamp Local]. Para soporte técnico o reportar inconsistencias en el origen, contactar al equipo de datos.

## 4. RECOMENDACIONES DE ARQUITECTURA PARA LA CAPA DE VISUALIZACIÓN

* Orquestación y Refresco Sincronizado: Una vez implementados los DAGs en la fase posterior, el pipeline debe disparar una petición API a Power BI Service mediante un Gateway de datos para asegurar el refresco de los tableros inmediatamente después de la ingesta batch/micro-batch.
* Seguridad a Nivel de Fila (RLS): Implementar Row-Level Security en Power BI. Esto asegurará que el área financiera visualice los impactos económicos y costos operativos, mientras que los gerentes de los CD vean únicamente sus rutas de despacho, unificando la verdad de los datos sin generar métricas contradictorias.
