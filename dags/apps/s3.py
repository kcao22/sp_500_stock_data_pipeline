import boto3

from airflow.models import Variable


def _choose_s3_bucket(is_test: bool, bucket: str):
    if is_test:
        match bucket.lower():
            case "ingress":
                return f""
                

def put_object(is_test: bool, target_bucket: str, key: str, body, **kwargs) -> None:
    if is_test:
        if not os.path.exists(key):
            os.path.makedirs(key)
    else:
        try:
            client = boto3.client(
                "s3",
                aws_access_key_id=Variable.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=Variable.get("AWS_SECRET_ACCESS_KEY"),
            )
            client.put_object(
                Bucket=target_bucket,
                Key=key,
                Body=body
            )
            
        except Exception as e:
            raise Exception(f"Failed to put object for {key} to bucket {target_bucket} with exception: {e}") from e
