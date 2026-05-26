# pipelines/tasks/metrics/feature_engineering.py
# Funciones de ingeniería de variables (feature engineering)
# Reciben un DataFrame y devuelven un DataFrame enriquecido con nuevas columnas
# El M2 puede importarlas con:
# from tasks.metrics.feature_engineering import agregar_trip_duration, agregar_z_score_duracion

import pandas as pd
import numpy as np


def agregar_trip_duration(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega la columna trip_duration_min al DataFrame de NYC Taxi.
    Calcula la duración del viaje en minutos entre pickup y dropoff.
    Elimina filas con fechas corruptas (NaT).

    Columnas requeridas: tpep_pickup_datetime, tpep_dropoff_datetime
    Columna nueva: trip_duration_min (float)
    """
    if df.empty:
        raise ValueError("El DataFrame está vacío.")

    if 'tpep_pickup_datetime' not in df.columns or 'tpep_dropoff_datetime' not in df.columns:
        raise KeyError("El DataFrame no tiene las columnas de datetime requeridas.")

    df = df.copy()

    # Conversión robusta de fechas con manejo de errores
    df['trip_duration_min'] = (
        pd.to_datetime(df['tpep_dropoff_datetime'], errors='coerce') -
        pd.to_datetime(df['tpep_pickup_datetime'], errors='coerce')
    ).dt.total_seconds() / 60

    filas_antes = len(df)
    # Eliminar filas con fechas corruptas
    df = df.dropna(subset=['trip_duration_min'])
    filas_despues = len(df)

    if filas_antes != filas_despues:
        print(f"[feature_engineering] Se eliminaron {filas_antes - filas_despues} filas con fechas corruptas.")

    return df


def agregar_z_score_duracion(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega la columna z_score_duracion al DataFrame de NYC Taxi.
    Requiere que trip_duration_min ya exista (correr agregar_trip_duration primero).

    Columna requerida: trip_duration_min (float)
    Columna nueva: z_score_duracion (float)
    """
    if df.empty:
        raise ValueError("El DataFrame está vacío.")

    if 'trip_duration_min' not in df.columns:
        raise KeyError("Falta la columna trip_duration_min. Corre agregar_trip_duration primero.")

    df = df.copy()

    media = df['trip_duration_min'].mean()
    std   = df['trip_duration_min'].std()

    if std == 0:
        df['z_score_duracion'] = 0.0
    else:
        df['z_score_duracion'] = np.abs((df['trip_duration_min'] - media) / std)

    return df