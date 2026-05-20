import pandas as pd

def clean_amazon_nulls(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica reglas de imputación específicas para Amazon Delivery.
    - Weather: rellena con "Unknown".
    - Agent_Rating: rellena con la media global.
    """
    print("Iniciando limpieza de nulos para Amazon Delivery...")

    # 1. Imputar Weather con "Unknown"
    weather_nulls = df['Weather'].isna().sum()
    df['Weather'] = df['Weather'].fillna('Unknown')
    print(f" - Weather nulos imputados: {weather_nulls}")

    # 2. Imputar Agent_Rating con la media
    rating_nulls = df['Agent_Rating'].isna().sum()
    if rating_nulls > 0:
        mean_rating = df['Agent_Rating'].mean()
        df['Agent_Rating'] = df['Agent_Rating'].fillna(mean_rating)
        print(f" - Agent_Rating nulos imputados: {rating_nulls} (con media {mean_rating:.2f})")

    return df