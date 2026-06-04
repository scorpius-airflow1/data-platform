import pandas as pd
import numpy as np

from tasks.metrics.feature_engineering import agregar_trip_duration, agregar_z_score_duracion


def calcular_kpis_nyc(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula KPIs de NYC Taxi agrupados por HORA del día para Power BI."""

    if df.empty:
        raise ValueError("El DataFrame de NYC Taxi está vacío. Verifica la capa clean/.")

    # 1. Feature Engineering
    df = agregar_trip_duration(df)
    df = agregar_z_score_duracion(df)

    # 2. Extraer la hora del día (Lo que M4 necesita)
    df['hora_dia'] = pd.to_datetime(df['tpep_pickup_datetime']).dt.hour

    # 3. Agrupar por hora y calcular KPIs
    def calcular_grupo_nyc(grupo):
        atipicas = (grupo['z_score_duracion'] > 3).sum()
        return pd.Series({
            'tiempo_promedio_ruta_min': round(grupo['trip_duration_min'].mean(), 2),
            'rutas_atipicas_count': int(atipicas),
            'costo_ineficiencia_usd': round(float(grupo.loc[grupo['z_score_duracion'] > 3, 'total_amount'].sum()), 2)
        })

    df_resultado = df.groupby('hora_dia', group_keys=False).apply(calcular_grupo_nyc, include_groups=False).reset_index()

    return df_resultado


def calcular_kpis_amazon(df: pd.DataFrame) -> dict:
    """Calcula KPIs de Amazon y devuelve un DICCIONARIO con dos DataFrames separados para Power BI."""

    if df.empty:
        raise ValueError("El DataFrame de Amazon Delivery está vacío. Verifica la capa clean/.")

    # 1. Vista por ZONA
    def calcular_grupo_zona(grupo):
        total = len(grupo)
        completadas = (grupo['Delivery_Time'] > 0).sum()
        fallidas = (grupo['Delivery_Time'] == 0).sum()
        return pd.Series({
            'tasa_entregas_completadas_pct': round((completadas / total) * 100, 2) if total > 0 else 0.0,
            'tasa_entregas_fallidas_pct': round((fallidas / total) * 100, 2) if total > 0 else 0.0,
            'zona_critica_retraso': float(grupo['Delivery_Time'].sum())
        })

    df_zona = df.groupby('Area', group_keys=False).apply(calcular_grupo_zona, include_groups=False).reset_index()
    df_zona = df_zona.rename(columns={'Area': 'zona'}) # M4 necesita la columna llamada 'zona'

    # 2. Vista por VEHÍCULO
    df_vehiculo = df.groupby('Vehicle', group_keys=False).size().reset_index(name='incidencias_por_vehiculo')
    df_vehiculo = df_vehiculo.rename(columns={'Vehicle': 'vehiculo'}) # M4 necesita la columna llamada 'vehiculo'
    df_vehiculo['incidencias_por_vehiculo'] = df_vehiculo['incidencias_por_vehiculo'].astype(float)

    # Devolvemos un diccionario para que el DAG los guarde como 2 archivos Parquet separados en S3
    return {
        "vista_zona": df_zona,
        "vista_vehiculo": df_vehiculo
    }