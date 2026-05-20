import pandas as pd

def filter_gps_valid(df: pd.DataFrame, lat_col: str, lon_col: str) -> pd.DataFrame:
    """
    Elimina filas con coordenadas fuera del rango del mundo.
    Lat: -90 a 90, Lon: -180 a 180.
    """
    # Validar que las columnas existan para evitar errores
    if lat_col not in df.columns or lon_col not in df.columns:
        return df

    # Filtros booleanos
    valid_lat = df[lat_col].between(-90, 90)
    valid_lon = df[lon_col].between(-180, 180)
    
    # Aplicar filtro (AND lógico)
    df_clean = df[valid_lat & valid_lon].copy()
    
    removed = len(df) - len(df_clean)
    if removed > 0:
        print(f" - Eliminados {removed} registros por GPS inválido.")
        
    return df_clean

def filter_positive_duration(df: pd.DataFrame, start_col: str, end_col: str) -> pd.DataFrame:
    """
    Asegura que la fecha fin sea posterior a la fecha inicio.
    """
    # Convertir a datetime si no lo son (para evitar errores de tipo string)
    df[start_col] = pd.to_datetime(df[start_col])
    df[end_col] = pd.to_datetime(df[end_col])
    
    # Filtro: Fin > Inicio
    mask = df[end_col] > df[start_col]
    df_clean = df[mask].copy()
    
    removed = len(df) - len(df_clean)
    if removed > 0:
        print(f" - Eliminados {removed} registros por tiempo inconsistente (duración <= 0).")
        
    return df_clean