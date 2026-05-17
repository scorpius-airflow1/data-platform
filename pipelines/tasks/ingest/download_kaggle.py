import os
import logging
import boto3

logger = logging.getLogger(__name__)

S3_BUCKET = "scorpius-airflow-logs-2026"


def verify_file_in_s3(s3_key: str) -> str:
    """
    Verifica que el archivo existe en S3.
    Retorna el s3_key si existe, lanza excepción si no.
    """
    from airflow.models import Variable

    s3 = boto3.client(
        "s3",
        region_name="us-east-2",
        aws_access_key_id=Variable.get("aws_access_key_id"),
        aws_secret_access_key=Variable.get("aws_secret_access_key"),
    )

    try:
        response = s3.head_object(Bucket=S3_BUCKET, Key=s3_key)
        size_mb = response["ContentLength"] / (1024 * 1024)
        logger.info(f"Archivo verificado: s3://{S3_BUCKET}/{s3_key} ({size_mb:.2f} MB)")
        return s3_key
    except Exception as e:
        raise FileNotFoundError(
            f"Archivo no encontrado en s3://{S3_BUCKET}/{s3_key}: {e}"
        )


def log_ingestion(s3_key: str, dataset_name: str) -> dict:
    """
    Registra la ingestión con metadata básica.
    Retorna un dict con la info del archivo ingerido.
    """
    from airflow.models import Variable
    import boto3

    s3 = boto3.client(
        "s3",
        region_name="us-east-2",
        aws_access_key_id=Variable.get("aws_access_key_id"),
        aws_secret_access_key=Variable.get("aws_secret_access_key"),
    )

    response = s3.head_object(Bucket=S3_BUCKET, Key=s3_key)

    metadata = {
        "dataset": dataset_name,
        "s3_key": s3_key,
        "size_bytes": response["ContentLength"],
        "size_mb": round(response["ContentLength"] / (1024 * 1024), 2),
        "last_modified": str(response["LastModified"]),
    }

    logger.info(f"Ingestión registrada: {metadata}")
    return metadata