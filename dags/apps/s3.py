import datetime
import boto3
import os


from apps.print_utils import print_logging_info_decorator


def _choose_s3_bucket(is_test: bool, bucket: str):
    if is_test:
        match bucket.lower():
            case "s3_ingress":
                return "ingress"
            case "s3_archive":
                return "archive"
            case _:
                raise ValueError(f"Invalid bucket name: {bucket}. Must be either 's3_ingress' or 's3_archive'.")
    else:
        match bucket.lower():
            case "s3_ingress":
                return "kc-prod-data-warehouse-ingress"
            case "s3_archive":
                return "kc-prod-data-warehouse-archive"
            case _:
                raise ValueError(f"Invalid bucket name: {bucket}. Must be either 's3_ingress' or 's3_archive'.")


def _create_client():
    client = boto3.client(
        "s3",
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    )
    return client


@print_logging_info_decorator(redacted_params=["body"])
def put_object(is_test: bool, bucket: str, key: str, body: str, **kwargs) -> None:
    """
    Puts object to target s3 bucket. If local, writes to a mimic bucket in /opt/airflow/files/.
    @param is_test: If True, then local. Else AWS prod environment.
    @param bucket: If local, the folder of interest. Else S3 target bucket name.
    @param key: Full prefix and name of file.
    @param body: Content of file.
    @param kwargs: Keyword arguments.
    @return: File key.
    """
    if key.startswith("/"):
        key = key[1:]
    if is_test:
        try:
            file_path = os.path.join("/opt/airflow/files/", _choose_s3_bucket(is_test=is_test, bucket=bucket), key)
            if not os.path.exists(file_path):
                os.makedirs(name=os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(body)
        except Exception as e:
            raise Exception(f"Failed to put object to target bucket {bucket} with object path {key}. Exception: {e}")
    else:
        try:
            client = _create_client()
            client.put_object(
                Bucket=_choose_s3_bucket(is_test=is_test, bucket=bucket),
                Key=key,
                Body=body,
                **kwargs
            )
        except Exception as e:
            raise Exception(f"Failed to put object for {key} to bucket {bucket} with exception: {e}") from e


@print_logging_info_decorator
def get_object(is_test: bool, bucket: str, key: str, **kwargs) -> dict:
    """
    Gets object from a bucket.
    @param is_test: If True, then local. Else AWS prod environment.
    @param bucket: Bucket name.
    @param key: Full path of the object.
    @param kwargs: Keyword arguments.
    @return: Object content.
    """
    if key.startswith("/"):
        key = key[1:]
    try:
        if is_test:
            file_path = os.path.join(
                "/opt/airflow/files/",
                _choose_s3_bucket(is_test=is_test, bucket=bucket),
                key
            )
            try:
                with open(file_path, "rb") as f:
                    return {"Body": f.read()}
            except UnicodeDecodeError:
                with open(file_path, "rb") as f:
                    return {"Body": f.read()}
        else:
            client = _create_client()
            return client.get_object(
                Bucket=_choose_s3_bucket(is_test=is_test, bucket=bucket),
                Key=key,
                **kwargs
            )
    except Exception as e:
        raise Exception(f"Failed to get object from bucket {bucket} with key {key}. Exception: {e}") from e


@print_logging_info_decorator
def copy_object(is_test: bool, source_bucket: str, source_key: str, target_bucket: str, target_key: str, **kwargs) -> None:
    """
    Copies object from a source bucket to target bucket.
    @param is_test: If True, then local. Else AWS prod environment.
    @param source_bucket: Source bucket name.
    @param source_key: Full path of the source object.
    @param target_bucket: Target bucket name.
    @param target_key: Full path of target object.
    @param kwargs: Keyword arguments.
    @return: None.
    """
    print(f"Getting object from bucket {source_bucket} with key {source_key}")
    try:
        if is_test:
            body = get_object(
                is_test=is_test,
                bucket=source_bucket,
                key=source_key
            )["Body"]
            put_object(
                is_test=is_test,
                bucket=target_bucket,
                key=target_key,
                body=body
            )
        else:
            source_bucket = _choose_s3_bucket(is_test=is_test, bucket=source_bucket)
            target_bucket = _choose_s3_bucket(is_test=is_test, bucket=target_bucket)
            client = _create_client()
            client.copy_object(
                Bucket=target_bucket,
                Key=target_key,
                CopySource={"Bucket": source_bucket, "Key": source_key},
            )
    except Exception as e:
        raise Exception(f"Failed to copy object from source bucket {source_bucket} with object path {source_key} to target bucket {target_bucket} with object path {target_key}. Exception: {e}") from e


@print_logging_info_decorator
def delete_object(is_test: bool, bucket: str, key: str, **kwargs) -> None:
    if key.startswith("/"):
        key = key[1:]
    try:
        if is_test:
            os.remove(os.path.join("/opt/airflow/files/", _choose_s3_bucket(is_test=is_test, bucket=bucket), key))
        else:
            client = _create_client()
            client.delete_object(
                Bucket=_choose_s3_bucket(is_test=is_test, bucket=bucket),
                Key=key,
                **kwargs
            )
    except Exception as e:
        raise Exception(f"Failed to delete object from bucket {bucket} with key {key}. Exception: {e}") from e


@print_logging_info_decorator
def download_file(is_test:bool, bucket: str, key: str, filename: str, **kwargs) -> None:
    """
    Downloads file from target S3 bucket to /tmp directory.
    """
    if key.startswith("/"):
        key = key[1:]
    try:
        if is_test:
            body = get_object(
                is_test=is_test, 
                bucket=bucket, 
                key=key
            )["Body"]
            if not os.path.exists("/tmp"):
                os.makedirs(name="/tmp", exist_ok=True)
            with open(f"/tmp/{os.path.basename(filename)}", "wb") as f:
                f.write(body)
            print(f"File downloaded to /tmp/{os.path.basename(filename)}")
            return f"/tmp/{os.path.basename(filename)}"
        else:
            client = _create_client()
            print(f"Key: {key}")
            print(f"Bucket: {_choose_s3_bucket(is_test=is_test, bucket=bucket)}")
            print(f"Is Test: {is_test}")
            client.download_file(
                Bucket=_choose_s3_bucket(is_test=is_test, bucket=bucket),
                Key=key,
                Filename=f"/tmp/{os.path.basename(filename)}",
                **kwargs
            )
            return f"/tmp/{os.path.basename(filename)}"
    except Exception as e:
        raise Exception(f"Failed to download file from bucket {bucket} with key {key}. Exception: {e}") from e


@print_logging_info_decorator
def list_objects(is_test: bool, bucket: str, prefix: str = ""):
    try:
        if is_test:
            files = {}
            for root, dirs, filenames in os.walk(os.path.join("/opt/airflow/files/", _choose_s3_bucket(is_test=is_test, bucket=bucket), prefix)):
                for filename in filenames:
                    file_m_time = os.path.getmtime(os.path.join(root, filename))
                    file_last_modified_datetime = datetime.datetime.fromtimestamp(file_m_time)
                    file_path = os.path.join(root, filename)
                    file_path = file_path.replace(os.path.join("/opt/airflow/files/", _choose_s3_bucket(is_test=is_test, bucket=bucket)), "")
                    files[file_path] = file_last_modified_datetime
            return {
                "Contents": [
                    {
                        "Key": file_path,
                        "LastModified": file_last_modified_datetime,
                    }
                    for file_path, file_last_modified_datetime in files.items()
                ]
            }
        else:
            client = _create_client()
            response = client.list_objects_v2(
                Bucket=_choose_s3_bucket(is_test=is_test, bucket=bucket),
                Prefix=prefix,
            )
            return response
    except Exception as e:
        raise Exception(f"Failed to list objects in bucket {bucket} with prefix {prefix}. Exception: {e}") from e


@print_logging_info_decorator
def get_most_recent_file(is_test: bool, bucket: str, prefix: str = "") -> str:
    files = list_objects(
        is_test=is_test,
        bucket=bucket,
        prefix=prefix
    )
    most_recent_file = {}
    for file in files["Contents"]:
        if most_recent_file == {}:
            most_recent_file = file
            continue
        elif file["LastModified"] > most_recent_file["LastModified"]:
            most_recent_file = file
    if most_recent_file and most_recent_file["Key"]:
        if most_recent_file["Key"].startswith("/"):
            most_recent_file["Key"] = most_recent_file["Key"][1:]
    print(f"Most recent file found from {bucket} with prefix {prefix}: {most_recent_file['Key']}")
    return most_recent_file["Key"] if most_recent_file else None
