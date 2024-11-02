import os
import time
from typing import List

import boto3
import aioboto3
from botocore.config import Config
from botocore.exceptions import ClientError


from api.blob.base import BaseStorage


class S3Storage(BaseStorage):
    def __init__(self, endpoint_url: str = "http://localhost:4566"):
        self.endpoint_url = endpoint_url
        self.config = Config(signature_version="s3v4")

        self.s3 = boto3.client(
            "s3",
            endpoint_url="http://localhost:4566",
            config=Config(signature_version="s3v4"),
        )

    async def delete_file(self, bucket_name: str, object_name: str) -> None:
        """Delete a file from the specified bucket

        Args:
            bucket_name (str):  Name of the bucket
            object_name (str):  Name of the object to delete

        Raises:
            Exception: _description_
        """
        # try:
        #     self.s3.delete_object(Bucket=bucket_name, Key=object_name)
        # except ClientError as e:
        #     raise Exception(f"Failed to delete file: {e}")
        async with aioboto3.client(
            "s3", endpoint_url=self.endpoint_url, config=self.config
        ) as s3:
            try:
                await s3.delete_object(Bucket=bucket_name, Key=object_name)
            except ClientError as e:
                raise Exception(f"Failed to delete file: {e}")

    async def generate_upload_signed_url(
        self, bucket_name: str, object_name: str
    ) -> str:
        """Generate a signed URL for uploading a file.

        Args:
            bucket_name (str): Name of the bucket.
            object_name (str): Name of the object to upload.

        Raises:
            Exception: If URL generation fails.

        Returns:
            str: Signed URL for uploading.
        """
        async with aioboto3.client(
            "s3", endpoint_url=self.endpoint_url, config=self.config
        ) as s3:
            try:
                return await s3.generate_presigned_url(
                    "put_object",
                    Params={"Bucket": bucket_name, "Key": object_name},
                    ExpiresIn=3600,
                )
            except ClientError as e:
                raise Exception(f"Failed to generate upload signed URL: {e}")

    async def generate_download_signed_url(
        self, bucket_name: str, object_name: str
    ) -> str:
        """Generate a signed URL for downloading a file.

        Args:
            bucket_name (str): Name of the bucket.
            object_name (str): Name of the object to download.

        Raises:
            Exception: If URL generation fails.

        Returns:
            str: Signed URL for downloading.
        """
        async with aioboto3.client(
            "s3", endpoint_url=self.endpoint_url, config=self.config
        ) as s3:
            try:
                return await s3.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": bucket_name, "Key": object_name},
                    ExpiresIn=3600,
                )
            except ClientError as e:
                raise Exception(f"Failed to generate download signed URL: {e}")
