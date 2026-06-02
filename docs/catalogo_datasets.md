# Catálogo de Datasets — Scorpius Data Platform

**Proyecto:** Pipeline de datos logísticos  
**Semana:** 1 — Ingesta | **Actualizado:** 2026-06-01 — Semana 2 (Clean y Curated).
**Autores:** M2 — Ingesta y limpieza, M3 (Feature Engineering y KPIs).
**Rama:** sirius  

---

## Resumen

| Dataset | Filas | Columnas | Tamaño | Formato |
|---|---|---|---|---|
| NYC Taxi Trip Records | 2,964,624 | 19 | 47.65 MB | PARQUET |
| Amazon Delivery Dataset | 43,739 | 16 | 5.69 MB | CSV |
| Supply Chain Dataset | 100 | 24 | 0.02 MB | CSV |

---

## Resumen de Capas (Semana 2)

| Capa | Rita en S3 | Descripciòn | 
|---|---|---|
| raw/ | s3://scorpius-airflow-logs-2026/raw/ | Datos crudos descargados de las fuentes originales. Sin modificaciones. |
| clean/ | s3://scorpius-airflow-logs-2026/clean/ | Datos limpios. Se eliminaron nulos, se corrigieron tipos y se filtraron columnas irrelevantes. |
| curated/ | s3://scorpius-airflow-logs-2026/curated/ | Datos enriquecidos y KPIs calculados. Listos para consumo en Power BI y Amazon Athena. | 

---

## NYC Taxi Trip Records

| Campo | Detalle |
|---|---|
| **Fuente** | https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet |
| **Capa S3** | `s3://scorpius-airflow-logs-2026/raw/nyc_taxi/2024/01/` |
| **Formato** | PARQUET |
| **Filas** | 2,964,624 |
| **Columnas** | 19 |
| **Tamaño en S3** | 47.65 MB |
| **Descripción** | Registros de viajes en taxi amarillo de Nueva York. Simula eventos de rutas y viajes de la flota logística. |

### Mapeo al problema de negocio

| Columnas clave | Problema que resuelve |
|---|---|
| Coordenadas GPS | Detectar errores geográficos y rutas ineficientes |
| Campos de tiempo/duración | Medir retrasos en entregas |
| Campos de estado/resultado | Entregas completadas vs fallidas |
| Campos de inventario | Diferencias entre inventario físico y digital |

### Capa raw/ — Columnas originales

| Columna | Tipo | Nulos | Nulos % | Valores Únicos |
|---|---|---|---|---|
| `VendorID` | int32 | 0 | 0.0% | 3 |
| `tpep_pickup_datetime` | datetime64[us] | 0 | 0.0% | 1575706 |
| `tpep_dropoff_datetime` | datetime64[us] | 0 | 0.0% | 1574780 |
| `passenger_count` | float64 | 140162 | 4.73% | 10 |
| `trip_distance` | float64 | 0 | 0.0% | 4489 |
| `RatecodeID` | float64 | 140162 | 4.73% | 7 |
| `store_and_fwd_flag` | str | 140162 | 4.73% | 2 |
| `PULocationID` | int32 | 0 | 0.0% | 260 |
| `DOLocationID` | int32 | 0 | 0.0% | 261 |
| `payment_type` | int64 | 0 | 0.0% | 5 |
| `fare_amount` | float64 | 0 | 0.0% | 8970 |
| `extra` | float64 | 0 | 0.0% | 48 |
| `mta_tax` | float64 | 0 | 0.0% | 8 |
| `tip_amount` | float64 | 0 | 0.0% | 4192 |
| `tolls_amount` | float64 | 0 | 0.0% | 1127 |
| `improvement_surcharge` | float64 | 0 | 0.0% | 5 |
| `total_amount` | float64 | 0 | 0.0% | 19241 |
| `congestion_surcharge` | float64 | 140162 | 4.73% | 6 |
| `Airport_fee` | float64 | 140162 | 4.73% | 3 |


### Unicidad del registro

No se identificó columna con unicidad absoluta — revisar manualmente

### Problemas de calidad detectados

- `passenger_count` tiene 4.73% de valores nulos
- `RatecodeID` tiene 4.73% de valores nulos
- `store_and_fwd_flag` tiene 4.73% de valores nulos
- `congestion_surcharge` tiene 4.73% de valores nulos
- `Airport_fee` tiene 4.73% de valores nulos
- No se detectaron filas duplicadas exactas

### Capa `clean/` — Columnas después de limpieza (Semana 2)
 
**Ruta:** `s3://scorpius-airflow-logs-2026/clean/nyc_taxi/`  
**Formato:** PARQUET | **Filas:** 2,964,624 | **Columnas:** 5
 
El proceso de limpieza eliminó columnas de baja relevancia analítica y estandarizó los tipos de datos. Solo se conservaron las columnas necesarias para el cálculo de KPIs.
 
| Columna | Tipo | Descripción |
|---|---|---|
| `tpep_pickup_datetime` | datetime64[us] | Fecha y hora de inicio del viaje. |
| `tpep_dropoff_datetime` | datetime64[us] | Fecha y hora de fin del viaje. |
| `passenger_count` | float64 | Número de pasajeros. Puede contener nulos residuales. |
| `trip_distance` | float64 | Distancia del viaje en millas. |
| `total_amount` | float64 | Monto total cobrado al pasajero en USD. |
 
### Capa `curated/` — Archivo: `nyc_enriched.parquet` (Semana 2)
 
**Ruta:** `s3://scorpius-airflow-logs-2026/curated/nyc_enriched.parquet`  
**Formato:** PARQUET | **Filas:** 2,963,754 | **Columnas:** 7
 
Contiene todas las columnas de `clean/` más dos columnas calculadas por el módulo `feature_engineering.py`. Las 870 filas eliminadas corresponden a registros con fechas corruptas.
 
| Columna | Tipo | Descripción |
|---|---|---|
| `tpep_pickup_datetime` | datetime64[us] | Fecha y hora de inicio del viaje. |
| `tpep_dropoff_datetime` | datetime64[us] | Fecha y hora de fin del viaje. |
| `passenger_count` | float64 | Número de pasajeros. |
| `trip_distance` | float64 | Distancia del viaje en millas. |
| `total_amount` | float64 | Monto total cobrado en USD. |
| `trip_duration_min` | float64 | **Columna calculada.** Duración del viaje en minutos. Fórmula: `(tpep_dropoff_datetime - tpep_pickup_datetime).total_seconds() / 60`. |
| `z_score_duracion` | float64 | **Columna calculada.** Qué tan atípica es la duración de un viaje respecto al promedio general. Fórmula: `ABS((trip_duration_min - media) / desviacion_estandar)`. Un valor mayor a 3 indica una ruta anómala. |
 
---


## Amazon Delivery Dataset

| Campo | Detalle |
|---|---|
| **Fuente** | Kaggle — Amazon Delivery Dataset |
| **Capa S3** | `s3://scorpius-airflow-logs-2026/raw/amazon_delivery/` |
| **Formato** | CSV |
| **Filas** | 43,739 |
| **Columnas** | 16 |
| **Tamaño en S3** | 5.69 MB |
| **Descripción** | Registros de entregas de Amazon. Simula el estado de entregas completadas vs fallidas. |

### Mapeo al problema de negocio

| Columnas clave | Problema que resuelve |
|---|---|
| Coordenadas GPS | Detectar errores geográficos y rutas ineficientes |
| Campos de tiempo/duración | Medir retrasos en entregas |
| Campos de estado/resultado | Entregas completadas vs fallidas |
| Campos de inventario | Diferencias entre inventario físico y digital |

### Capa `raw/` — Columnas originales

| Columna | Tipo | Nulos | Nulos % | Valores Únicos |
|---|---|---|---|---|
| `Order_ID` | str | 0 | 0.0% | 43739 |
| `Agent_Age` | int64 | 0 | 0.0% | 22 |
| `Agent_Rating` | float64 | 54 | 0.12% | 28 |
| `Store_Latitude` | float64 | 0 | 0.0% | 521 |
| `Store_Longitude` | float64 | 0 | 0.0% | 415 |
| `Drop_Latitude` | float64 | 0 | 0.0% | 4367 |
| `Drop_Longitude` | float64 | 0 | 0.0% | 4367 |
| `Order_Date` | str | 0 | 0.0% | 44 |
| `Order_Time` | str | 0 | 0.0% | 177 |
| `Pickup_Time` | str | 0 | 0.0% | 193 |
| `Weather` | str | 91 | 0.21% | 6 |
| `Traffic` | str | 0 | 0.0% | 5 |
| `Vehicle` | str | 0 | 0.0% | 4 |
| `Area` | str | 0 | 0.0% | 4 |
| `Delivery_Time` | int64 | 0 | 0.0% | 89 |
| `Category` | str | 0 | 0.0% | 16 |


### Unicidad del registro

`Order_ID`

### Problemas de calidad detectados

- `Agent_Rating` tiene 0.12% de valores nulos
- `Weather` tiene 0.21% de valores nulos
- No se detectaron filas duplicadas exactas

### Capa `clean/` — Columnas después de limpieza (Semana 2)
 
**Ruta:** `s3://scorpius-airflow-logs-2026/clean/amazon_delivery/`  
**Formato:** PARQUET | **Filas:** 43,739 | **Columnas:** 16
 
Se conservaron todas las columnas originales. Se corrigieron los tipos de datos de las columnas de tiempo y se estandarizaron los nulos residuales.
 
| Columna | Tipo | Descripción |
|---|---|---|
| `Order_ID` | str | Identificador único de la orden. |
| `Agent_Age` | int64 | Edad del agente de entrega. |
| `Agent_Rating` | float64 | Calificación del agente (0-5). Puede contener nulos residuales. |
| `Store_Latitude` | float64 | Latitud GPS de la tienda de origen. |
| `Store_Longitude` | float64 | Longitud GPS de la tienda de origen. |
| `Drop_Latitude` | float64 | Latitud GPS del punto de entrega. |
| `Drop_Longitude` | float64 | Longitud GPS del punto de entrega. |
| `Order_Date` | str | Fecha en que se realizó la orden. |
| `Order_Time` | str | Hora en que se realizó la orden. |
| `Pickup_Time` | str | Hora en que el agente recogió el pedido. |
| `Weather` | str | Condición climática. Valores: `Sunny`, `Cloudy`, `Rainy`, `Windy`, `Foggy`, `Sandstorms`. |
| `Traffic` | str | Nivel de tráfico. Valores: `Low`, `Medium`, `High`, `Jam`. |
| `Vehicle` | str | Tipo de vehículo. Valores: `motorcycle`, `scooter`, `bicycle`, `van`. |
| `Area` | str | Zona geográfica. Valores: `Metropolitian`, `Urban`, `Semi-Urban`, `Other`. |
| `Delivery_Time` | int64 | Tiempo de entrega en minutos desde la recogida hasta la entrega. |
| `Category` | str | Categoría del producto entregado (16 categorías). |
 
### Capa `curated/` — Archivo: `amazon_enriched.parquet` (Semana 2)
 
**Ruta:** `s3://scorpius-airflow-logs-2026/curated/amazon_enriched.parquet`  
**Formato:** PARQUET | **Filas:** 43,739 | **Columnas:** 17
 
Contiene todas las columnas de `clean/` más una columna calculada que clasifica cada entrega según su tiempo.
 
| Columna nueva | Tipo | Descripción |
|---|---|---|
| `categoria_entrega` | str | **Columna calculada.** Clasifica la entrega según su tiempo: `Rápido` (por debajo del promedio), `Normal` (dentro del rango esperado), `Crítico` (Z-score > 3, tiempo muy superior al promedio). |
 
---


## Supply Chain Dataset

| Campo | Detalle |
|---|---|
| **Fuente** | Kaggle — Supply Chain Analysis Dataset |
| **Capa S3** | `s3://scorpius-airflow-logs-2026/raw/supply_chain/` |
| **Formato** | CSV |
| **Filas** | 100 |
| **Columnas** | 24 |
| **Tamaño en S3** | 0.02 MB |
| **Descripción** | Datos de cadena de suministro e inventario. Simula diferencias entre inventario físico y digital. |

### Mapeo al problema de negocio

| Columnas clave | Problema que resuelve |
|---|---|
| Coordenadas GPS | Detectar errores geográficos y rutas ineficientes |
| Campos de tiempo/duración | Medir retrasos en entregas |
| Campos de estado/resultado | Entregas completadas vs fallidas |
| Campos de inventario | Diferencias entre inventario físico y digital |

### Capa `raw/` — Columnas originales

| Columna | Tipo | Nulos | Nulos % | Valores Únicos |
|---|---|---|---|---|
| `Product type` | str | 0 | 0.0% | 3 |
| `SKU` | str | 0 | 0.0% | 100 |
| `Price` | float64 | 0 | 0.0% | 100 |
| `Availability` | int64 | 0 | 0.0% | 63 |
| `Number of products sold` | int64 | 0 | 0.0% | 96 |
| `Revenue generated` | float64 | 0 | 0.0% | 100 |
| `Customer demographics` | str | 0 | 0.0% | 4 |
| `Stock levels` | int64 | 0 | 0.0% | 65 |
| `Lead times` | int64 | 0 | 0.0% | 29 |
| `Order quantities` | int64 | 0 | 0.0% | 61 |
| `Shipping times` | int64 | 0 | 0.0% | 10 |
| `Shipping carriers` | str | 0 | 0.0% | 3 |
| `Shipping costs` | float64 | 0 | 0.0% | 100 |
| `Supplier name` | str | 0 | 0.0% | 5 |
| `Location` | str | 0 | 0.0% | 5 |
| `Lead time` | int64 | 0 | 0.0% | 29 |
| `Production volumes` | int64 | 0 | 0.0% | 96 |
| `Manufacturing lead time` | int64 | 0 | 0.0% | 30 |
| `Manufacturing costs` | float64 | 0 | 0.0% | 100 |
| `Inspection results` | str | 0 | 0.0% | 3 |
| `Defect rates` | float64 | 0 | 0.0% | 100 |
| `Transportation modes` | str | 0 | 0.0% | 4 |
| `Routes` | str | 0 | 0.0% | 3 |
| `Costs` | float64 | 0 | 0.0% | 100 |


### Unicidad del registro

`SKU`, `Price`, `Revenue generated`, `Shipping costs`, `Manufacturing costs`, `Defect rates`, `Costs`

### Problemas de calidad detectados

- No se detectaron filas duplicadas exactas

**Nota Semana 2:** Este dataset no fue procesado en la Semana 2. No existe versión en `clean/` ni en `curated/` todavía.

---

## KPIs Resumidos (Semana 2)
 
### Capa `curated/` — Archivo: `kpis_summary.parquet`
 
**Ruta:** `s3://scorpius-airflow-logs-2026/curated/kpis_summary.parquet`  
**Formato:** PARQUET | **Filas:** 21 | **Columnas:** 6
 
Tabla de KPIs calculados por `calculate_kpis.py`. Cada fila representa un indicador para una dimensión específica. Este archivo es la fuente principal del dashboard en Power BI.
 
| Columna | Tipo | Descripción |
|---|---|---|
| `kpi` | str | Nombre del indicador. |
| `valor` | float64 | Valor numérico del indicador. |
| `dataset` | str | Dataset de origen. Valores: `nyc_taxi`, `amazon_delivery`. |
| `tipo_dimension` | str | Categoría de agrupación. Valores: `zona_geografica`, `tipo_vehiculo`, `global`. |
| `valor_dimension` | str | Valor específico de la dimensión. Ejemplo: `Urban`, `motorcycle`, `global`. |
| `fecha_calculo` | datetime64 | Timestamp de cuándo se calculó el KPI. Útil para filtros temporales en Power BI. |
 
### Tabla de KPIs
 
| KPI | Dataset | Dimensión | Descripción |
|---|---|---|---|
| `tiempo_promedio_ruta_min` | nyc_taxi | global | Promedio de duración de todos los viajes en minutos. |
| `std_tiempo_viaje_min` | nyc_taxi | global | Desviación estándar de la duración. Mide la variabilidad. |
| `rutas_atipicas_count` | nyc_taxi | global | Viajes con Z-score de duración mayor a 3 (cuellos de botella). |
| `costo_ineficiencia_usd` | nyc_taxi | global | Suma del `total_amount` de los viajes atípicos en USD. |
| `pct_registros_duplicados` | nyc_taxi | global | Porcentaje de filas duplicadas exactas. |
| `tasa_entregas_completadas_pct` | amazon_delivery | zona_geografica | Porcentaje de entregas completadas por zona. |
| `tasa_entregas_fallidas_pct` | amazon_delivery | zona_geografica | Porcentaje de entregas fallidas por zona. |
| `zona_critica_retraso` | amazon_delivery | zona_geografica | Tiempo de entrega acumulado por zona. Mayor valor = zona más crítica. |
| `incidencias_por_vehiculo` | amazon_delivery | tipo_vehiculo | Cantidad de entregas por tipo de vehículo. |
 
---
 
## Glosario Técnico
 
| Término | Definición |
|---|---|
| **Z-score** | Medida que indica cuántas desviaciones estándar se aleja un valor del promedio. Un Z-score > 3 se considera una anomalía. |
| **Feature Engineering** | Proceso de crear nuevas columnas calculadas a partir de datos existentes para facilitar el análisis. |
| **DAG** | Directed Acyclic Graph. Unidad de trabajo en Airflow que define el orden de ejecución de las tareas del pipeline. |
| **Capa raw/** | Datos tal como llegaron de la fuente. No se modifican nunca. |
| **Capa clean/** | Datos limpios y estandarizados. Sin nulos críticos ni tipos incorrectos. |
| **Capa curated/** | Datos listos para análisis. Incluyen columnas calculadas y KPIs agregados. |
