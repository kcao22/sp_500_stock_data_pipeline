import boto3
import os

from airflow.models import Variable


def _choose_s3_bucket(is_test: bool, bucket: str):
    if is_test:
        match bucket.lower():
            case "s3_ingress":
                return "ingress"
            case "s3_archive":
                return "archive"


def put_object(is_test: bool, target_bucket: str, key: str, body: str, **kwargs) -> None:
    """
    Puts object to target s3 bucket. If local, writes to a mimic bucket in /opt/airflow/files/.
    @param is_test: If True, then local. Else AWS prod environment.
    @param target_bucket: If local, the folder of interest. Else S3 target bucket name.
    @param key: Full prefix and name of file.
    @param body: Content of file.
    @param kwargs: Keyword arguments.
    @return: File key.
    """
    if is_test:
        try:
            file_path = os.path.join("/opt/airflow/files/", key)
            if not os.path.exists(file_path):
                os.makedirs(name=os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(body)
        except Exception as e:
            raise Exception(f"Failed to put object to target bucket {target_bucket} with object path {key}.")
    else:
        try:
            client = boto3.client(
                "s3",
                aws_access_key_id=Variable.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=Variable.get("AWS_SECRET_ACCESS_KEY"),
            )
            client.put_object(
                Bucket=_choose_s3_bucket(is_test=is_test, bucket=target_bucket),
                Key=key,
                Body=body
            )
        except Exception as e:
            raise Exception(f"Failed to put object for {key} to bucket {target_bucket} with exception: {e}") from e
