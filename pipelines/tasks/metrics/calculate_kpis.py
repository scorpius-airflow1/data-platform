# Estas funciones deben leer un DataFrame (limpio)
# y devolver un nuevo DataFrame resumido
# Salida optimizada para consumo en Power BI

import pandas as pd
import numpy as np

from pipelines.tasks.metrics.feature_engineering import agregar_trip_duration, agregar_z_score_duracion


def calcular_kpis_nyc(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula KPIs 1, 2, 5, 7, 8 desde NYC Taxi."""

    if df.empty:
        raise ValueError("El DataFrame de NYC Taxi está vacío. Verifica la capa clean/.")

    # Ahora usa las funciones de feature_engineering en lugar de calcular aquí
    df = agregar_trip_duration(df)
    df = agregar_z_score_duracion(df)


    # KPI 1 y 2
    kpi1 = df['trip_duration_min'].mean()
    kpi2 = df['trip_duration_min'].std()    

    # KPI 7 y KPI 5: protegidos contra desviación estándar = 0
    if kpi2 == 0:
        kpi7 = 0
        kpi5 = 0.0
    else:
        kpi7 = int((df['z_score_duracion'] > 3).sum())
        kpi5 = float(df.loc[df['z_score_duracion'] > 3, 'total_amount'].sum())

    # KPI 8: Porcentaje de duplicados
    total = len(df)
    duplicados = int(df.duplicated().sum())
    kpi8 = round((duplicados / total) * 100, 2) if total > 0 else 0

    return pd.DataFrame([{
        'kpi': 'tiempo_promedio_ruta_min',  'valor': round(kpi1, 2), 'dataset': 'nyc_taxi', 'tipo_dimension': 'global', 'valor_dimension': 'global', 'fecha_calculo': pd.Timestamp.now()
    }, {
        'kpi': 'std_tiempo_viaje_min',       'valor': round(kpi2, 2), 'dataset': 'nyc_taxi', 'tipo_dimension': 'global', 'valor_dimension': 'global', 'fecha_calculo': pd.Timestamp.now()
    }, {
        'kpi': 'rutas_atipicas_count',       'valor': float(kpi7),    'dataset': 'nyc_taxi', 'tipo_dimension': 'global', 'valor_dimension': 'global', 'fecha_calculo': pd.Timestamp.now()
    }, {
        'kpi': 'costo_ineficiencia_usd',     'valor': round(kpi5, 2), 'dataset': 'nyc_taxi', 'tipo_dimension': 'global', 'valor_dimension': 'global', 'fecha_calculo': pd.Timestamp.now()
    }, {
        'kpi': 'pct_registros_duplicados',   'valor': float(kpi8),    'dataset': 'nyc_taxi', 'tipo_dimension': 'global', 'valor_dimension': 'global', 'fecha_calculo': pd.Timestamp.now()
    }])


def calcular_kpis_amazon(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula KPIs 3, 4, 9, 10 desde Amazon Delivery agrupados por dimensión."""

    if df.empty:
        raise ValueError("El DataFrame de Amazon Delivery está vacío. Verifica la capa clean/.")

    timestamp = pd.Timestamp.now()

    # KPI 3 y 4: Tasa de entregas completadas y fallidas POR ZONA
    tasa_por_zona = (
        df.groupby('Area')
        .apply(lambda x: pd.Series({
            'completadas': round((x['Delivery_Time'] > 0).sum() / len(x) * 100, 2),
            'fallidas':    round((x['Delivery_Time'] == 0).sum() / len(x) * 100, 2)
        }))
        .reset_index()
    )

    kpi3 = tasa_por_zona[['Area', 'completadas']].rename(
        columns={'Area': 'valor_dimension', 'completadas': 'valor'}
    )
    kpi3['kpi']             = 'tasa_entregas_completadas_pct'
    kpi3['tipo_dimension']  = 'zona_geografica'
    kpi3['dataset']         = 'amazon_delivery'
    kpi3['fecha_calculo']   = timestamp

    kpi4 = tasa_por_zona[['Area', 'fallidas']].rename(
        columns={'Area': 'valor_dimension', 'fallidas': 'valor'}
    )
    kpi4['kpi']             = 'tasa_entregas_fallidas_pct'
    kpi4['tipo_dimension']  = 'zona_geografica'
    kpi4['dataset']         = 'amazon_delivery'
    kpi4['fecha_calculo']   = timestamp

    # KPI 9: Zonas críticas (ya estaba por zona, solo se ajusta estructura)
    kpi9 = (
        df.groupby('Area')['Delivery_Time']
        .sum()
        .reset_index()
        .rename(columns={'Area': 'valor_dimension', 'Delivery_Time': 'valor'})
        .sort_values('valor', ascending=False)
        .head(5)
    )
    kpi9['kpi']             = 'zona_critica_retraso'
    kpi9['tipo_dimension']  = 'zona_geografica'
    kpi9['dataset']         = 'amazon_delivery'
    kpi9['fecha_calculo']   = timestamp
    kpi9['valor']           = kpi9['valor'].astype(float)

    # KPI 10: Incidencias por vehículo (ya estaba por vehículo, solo se ajusta estructura)
    kpi10 = (
        df.groupby('Vehicle')
        .size()
        .reset_index(name='valor')
        .rename(columns={'Vehicle': 'valor_dimension'})
    )
    kpi10['kpi']            = 'incidencias_por_vehiculo'
    kpi10['tipo_dimension'] = 'tipo_vehiculo'
    kpi10['dataset']        = 'amazon_delivery'
    kpi10['fecha_calculo']  = timestamp
    kpi10['valor']          = kpi10['valor'].astype(float)

    return pd.concat([kpi3, kpi4, kpi9, kpi10], ignore_index=True)