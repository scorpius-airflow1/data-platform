import os
import boto3
import requests
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

NYC_TAXI_URL = (
    "https://d37ci6vzurychx.cloudfront.net/trip-data/"
    "yellow_tripdata_{year}-{month:02d}.parquet"
)

S3_BUCKET = "scorpius-airflow-logs-2026"
S3_PREFIX = "raw/nyc_taxi"


def download_nyc_taxi(year: int, month: int, tmp_dir: str = "/tmp") -> str:
    url = NYC_TAXI_URL.format(year=year, month=month)
    filename = f"yellow_tripdata_{year}-{month:02d}.parquet"
    local_path = Path(tmp_dir) / filename

    logger.info(f"Descargando desde: {url}")
    response = requests.get(url, stream=True, timeout=120)
    response.raise_for_status()

    with open(local_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    logger.info(f"Archivo guardado en: {local_path}")
    return str(local_path)


def upload_to_s3(local_path: str, year: int, month: int) -> str:
    filename = Path(local_path).name
    s3_key = f"{S3_PREFIX}/{year}/{month:02d}/{filename}"

    logger.info(f"Subiendo a s3://{S3_BUCKET}/{s3_key}")

    s3 = boto3.client(
        "s3",
        region_name="us-east-2",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    )
    s3.upload_file(local_path, S3_BUCKET, s3_key)

    logger.info(f"Upload completado: {s3_key}")
    return s3_key


def cleanup_local(local_path: str) -> None:
    Path(local_path).unlink(missing_ok=True)
    logger.info(f"Temporal eliminado: {local_path}")