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
        'kpi':            'tiempo_promedio_ruta_min',
        'valor':          round(kpi1, 2),
        'dataset':        'nyc_taxi',
        'zona':           'global',
        'fecha_calculo':  pd.Timestamp.now()
    }, {
        'kpi':            'std_tiempo_viaje_min',
        'valor':          round(kpi2, 2),
        'dataset':        'nyc_taxi',
        'zona':           'global',
        'fecha_calculo':  pd.Timestamp.now()
    }, {
        'kpi':            'rutas_atipicas_count',
        'valor':          float(kpi7),
        'dataset':        'nyc_taxi',
        'zona':           'global',
        'fecha_calculo':  pd.Timestamp.now()
    }, {
        'kpi':            'costo_ineficiencia_usd',
        'valor':          round(kpi5, 2),
        'dataset':        'nyc_taxi',
        'zona':           'global',
        'fecha_calculo':  pd.Timestamp.now()
    }, {
        'kpi':            'pct_registros_duplicados',
        'valor':          float(kpi8),
        'dataset':        'nyc_taxi',
        'zona':           'global',
        'fecha_calculo':  pd.Timestamp.now()
    }])


def calcular_kpis_amazon(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula KPIs 3, 4, 9, 10 desde Amazon Delivery."""

    if df.empty:
        raise ValueError("El DataFrame de Amazon Delivery está vacío. Verifica la capa clean/.")

    total = len(df)
    timestamp = pd.Timestamp.now()

    # KPI 3 y 4: Tasa de entregas
    completadas = int((df['Delivery_Time'] > 0).sum())
    fallidas = total - completadas
    kpi3 = round((completadas / total) * 100, 2) if total > 0 else 0
    kpi4 = round((fallidas / total) * 100, 2) if total > 0 else 0

    # KPI 9: Zonas críticas con mayor tiempo acumulado
    zonas = (
        df.groupby('Area')['Delivery_Time']
        .sum()
        .reset_index()
        .rename(columns={'Area': 'zona', 'Delivery_Time': 'valor'})
        .sort_values('valor', ascending=False)
        .head(5)
    )
    zonas['kpi']           = 'zona_critica_retraso'
    zonas['dataset']       = 'amazon_delivery'
    zonas['fecha_calculo'] = timestamp
    zonas['valor']         = zonas['valor'].astype(float)

    # KPI 10: Incidencias por vehículo
    incidencias = (
        df.groupby('Vehicle')
        .size()
        .reset_index(name='valor')
        .rename(columns={'Vehicle': 'zona'})
    )
    incidencias['kpi']           = 'incidencias_por_vehiculo'
    incidencias['dataset']       = 'amazon_delivery'
    incidencias['fecha_calculo'] = timestamp
    incidencias['valor']         = incidencias['valor'].astype(float)

    # KPIs globales
    resumen = pd.DataFrame([{
        'kpi':           'tasa_entregas_completadas_pct',
        'valor':         float(kpi3),
        'dataset':       'amazon_delivery',
        'zona':          'global',
        'fecha_calculo': timestamp
    }, {
        'kpi':           'tasa_entregas_fallidas_pct',
        'valor':         float(kpi4),
        'dataset':       'amazon_delivery',
        'zona':          'global',
        'fecha_calculo': timestamp
    }])

    return pd.concat([resumen, zonas, incidencias], ignore_index=True)