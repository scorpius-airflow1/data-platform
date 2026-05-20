import pandas as pd

def clean_nyc_nulls(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica reglas de imputación específicas para NYC Taxi.
    - passenger_count: rellena con 1.
    - congestion_surcharge y Airport_fee: rellenan con 0.
    """
    print("Iniciando limpieza de nulos para NYC Taxi...")
    
    # 1. Imputar passenger_count con 1 (asumimos viaje individual)
    # Usamos .fillna() directamente
    initial_count = df['passenger_count'].isna().sum()
    df['passenger_count'] = df['passenger_count'].fillna(1.0)
    print(f" - Pasajeros nulos imputados: {initial_count}")

    # 2. Imputar cargos adicionales con 0.0
    surcharge_cols = ['congestion_surcharge', 'Airport_fee']
    for col in surcharge_cols:
        if col in df.columns:
            initial_nulls = df[col].isna().sum()
            df[col] = df[col].fillna(0.0)
            print(f" - {col} nulos imputados: {initial_nulls}")

    return df