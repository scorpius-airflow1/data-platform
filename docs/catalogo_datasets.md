# Catálogo de Datasets — Scorpius Data Platform

**Proyecto:** Pipeline de datos logísticos  
**Semana:** 1 — Ingesta  
**Generado:** 2026-05-17 12:38  
**Autor:** Miembro 2 — Ingesta  
**Rama:** sirius  

---

## Resumen

| Dataset | Filas | Columnas | Tamaño | Formato |
|---|---|---|---|---|
| NYC Taxi Trip Records | 2,964,624 | 19 | 47.65 MB | PARQUET |
| Amazon Delivery Dataset | 43,739 | 16 | 5.69 MB | CSV |
| Supply Chain Dataset | 100 | 24 | 0.02 MB | CSV |

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

### Columnas

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

### Columnas

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

### Columnas

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

---
