1. Dataset: NYC Taxi Trip Records
Fuente: Yellow Taxi Enero 2024

Regla 1.1: Limpieza de Pasajeros (Nulos)
Columna: passenger_count
Problema: Tiene 4.73% de valores nulos (140,162 filas).
Acción Correctiva: Imputar con valor 1. (Asumimos que si no se registró, era un viaje individual).
Justificación: Perdemos mucha información si eliminamos el 5% de los datos.
Regla 1.2: Limpieza de Tarifas (Nulos)
Columnas: congestion_surcharge, Airport_fee
Problema: Ambas tienen 4.73% de nulos.
Acción Correctiva: Imputar con valor 0.0.
Justificación: Si no hay registro, se asume que no hubo recargo adicional.
Regla 1.3: Consistencia Temporal
Columnas: tpep_pickup_datetime, tpep_dropoff_datetime
Problema: No se detectaron nulos, pero debemos validar lógica.
Condición de error: tpep_dropoff_datetime <= tpep_pickup_datetime.
Acción Correctiva: ELIMINAR la fila. El tiempo de viaje no puede ser negativo o cero.
Regla 1.4: Valores Lógicos de Distancia y Monto
Columnas: trip_distance, total_amount
Condición de error: trip_distance <= 0 OR total_amount <= 0.
Acción Correctiva: ELIMINAR. Un viaje pago y con distancia recorrida debe ser mayor a cero.


2. Dataset: Amazon Delivery Dataset
Fuente: Kaggle

Regla 2.1: Unicidad
Columna: Order_ID
Estado: El Miembro 2 confirmó que es la llave única y no hay duplicados.
Acción: Mantener validación en código por seguridad (drop_duplicates(subset=['Order_ID'])).
Regla 2.2: Limpieza de Clima (Nulos)
Columna: Weather
Problema: Tiene 0.21% de nulos (91 filas).
Acción Correctiva: Reemplazar nulos con string "Unknown".
Justificación: Es una variable categórica crítica; no podemos inventar el clima, pero "Unknown" es una categoría válida para análisis posterior.
Regla 2.3: Limpieza de Rating del Agente (Nulos)
Columna: Agent_Rating
Problema: Tiene 0.12% de nulos (54 filas).
Acción Correctiva: Imputar con la media (promedio) de la columna Agent_Rating.
Justificación: Es muy poco porcentaje, usar la media no distorsionará el análisis global.
Regla 2.4: Validación de GPS
Columnas: Store_Latitude, Store_Longitude, Drop_Latitude, Drop_Longitude
Problema: Los catálogos no reportaron nulos, pero debemos validar rangos.
Condición de error: Latitud fuera de [-90, 90] O Longitud fuera de [-180, 180].
Acción Correctiva: ELIMINAR. Coordenadas inválidas romperían mapas y cálculos de distancia.
Regla 2.5: Conversión y Validación de Tiempos
Columnas: Order_Time, Pickup_Time (Son tipo String/Texto), Delivery_Time (Int).
Problema: Order_Time y Pickup_Time vienen como texto. Necesitamos asegurarnos que el pickup sea después del orden.
Acción Correctiva:
Convertir columnas de texto a formato datetime.
Verificar que Pickup_Time > Order_Time (para el mismo día/registro).
Asegurar Delivery_Time > 0.


3. Dataset: Supply Chain Dataset
Fuente: Kaggle

Regla 3.1: Validación de Inventario (Stock)
Columna: Stock levels
Problema: No hay nulos reportados, pero validar lógica física.
Condición de error: Stock levels < 0.
Acción Correctiva: Reemplazar con 0. No puede existir stock negativo físico.
Regla 3.2: Valores Financieros Positivos
Columnas: Price, Shipping costs, Manufacturing costs, Costs
Condición de error: Cualquier valor < 0.
Acción Correctiva: ELIMINAR o revisar (Costos negativos indican errores de carga o devoluciones mal registradas, en este contexto de "pérdida de dinero" asumiremos error).
Estrategia de Ejecución en Python (Pipelines)
Para implementar estas reglas en la carpeta pipelines/tasks/quality/:

deduplicate.py: Usar Order_ID para Amazon. Para NYC, no hay ID único, por lo que no ejecutaremos deduplicación a menos que definamos una combinación de columnas compleja (por ahora se omite según catálogo).
handle_nulls.py:
Función impute_nyc_nulls(df): Llena passenger_count con 1 y cargos con 0.
Función impute_amazon_nulls(df): Llena Weather con "Unknown" y Agent_Rating con la media.
validate_logic.py:
Función filter_invalid_times(df, start_col, end_col): Elimina fechas fin < inicio.
Función filter_gps(df, lat_col, lon_col): Elimina coordenadas fuera de rango.