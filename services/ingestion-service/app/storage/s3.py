"""Thin wrapper around boto3's S3 client, pointed at MinIO for local dev.

Kept synchronous (boto3 has no first-class async API) and called from
FastAPI's threadpool via `run_in_threadpool`, and directly from Celery
workers (which are sync by nature).
"""

from functools import lru_cache
from typing import BinaryIO

import boto3
from botocore.client import Config as BotoConfig
from botocore.exceptions import ClientError

from app.config import Settings, get_settings


class ObjectStorage:
    def __init__(self, settings: Settings):
        self._bucket = settings.s3_bucket
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region,
            use_ssl=settings.s3_use_ssl,
            config=BotoConfig(signature_version="s3v4"),
        )

    def ensure_bucket(self) -> None:
        try:
            self._client.head_bucket(Bucket=self._bucket)
        except ClientError:
            self._client.create_bucket(Bucket=self._bucket)

    def put_object(self, key: str, body: BinaryIO, content_type: str) -> None:
        self._client.upload_fileobj(
            body, self._bucket, key, ExtraArgs={"ContentType": content_type}
        )

    def get_object_bytes(self, key: str) -> bytes:
        response = self._client.get_object(Bucket=self._bucket, Key=key)
        return response["Body"].read()

    def delete_object(self, key: str) -> None:
        self._client.delete_object(Bucket=self._bucket, Key=key)

    def presigned_get_url(self, key: str, expires_in: int = 900) -> str:
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket, "Key": key},
            ExpiresIn=expires_in,
        )

    @property
    def bucket(self) -> str:
        return self._bucket


@lru_cache
def get_object_storage() -> ObjectStorage:
    return ObjectStorage(get_settings())
