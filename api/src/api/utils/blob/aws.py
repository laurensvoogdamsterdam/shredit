import os
import time
from typing import List

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from api.utils.blob.base import BaseStorage


class S3Storage(BaseStorage):
    def __init__(self, endpoint_url: str = "http://localhost:4566"):
        self.s3 = boto3.client(
            "s3", endpoint_url=endpoint_url, config=Config(signature_version="s3v4")
        )

    def upload_file(self, file_path: str, bucket_name: str, object_name: str) -> str:
        """Upload a file to the specified bucket.

        Args:
            file_path (str): _description_
            bucket_name (str): _description_
            object_name (str): _description_

        Raises:
            Exception: _description_

        Returns:
            str: _description_
        """
        try:
            self.s3.upload_file(file_path, bucket_name, object_name)
            return f"{object_name} uploaded to {bucket_name}."
        except ClientError as e:
            raise Exception(f"Failed to upload file: {e}")

    def download_file(
        self, bucket_name: str, object_name: str, download_path: str
    ) -> None:
        """Download a file from the specified bucket.

        Args:
            bucket_name (str): _description_
            object_name (str): _description_
            download_path (str): _description_

        Raises:
            Exception: _description_
        """
        try:
            self.s3.download_file(bucket_name, object_name, download_path)
        except ClientError as e:
            raise Exception(f"Failed to download file: {e}")

    def delete_file(self, bucket_name: str, object_name: str) -> None:
        """Delete a file from the specified bucket

        Args:
            bucket_name (str):  Name of the bucket
            object_name (str):  Name of the object to delete

        Raises:
            Exception: _description_
        """
        try:
            self.s3.delete_object(Bucket=bucket_name, Key=object_name)
        except ClientError as e:
            raise Exception(f"Failed to delete file: {e}")

    def list_files(self, bucket_name: str) -> List[str]:
        """List all files in the specified bucket.

        Args:
            bucket_name (str): _description_

        Raises:
            Exception: _description_

        Returns:
            List[str]: _description_
        """
        try:
            response = self.s3.list_objects_v2(Bucket=bucket_name)
            if "Contents" in response:
                return [obj["Key"] for obj in response["Contents"]]
            return []
        except ClientError as e:
            raise Exception(f"Failed to list files: {e}")

    def generate_upload_signed_url(self, bucket_name: str, object_name: str) -> str:
        """Generate a signed URL for uploading a file.

        Args:
            bucket_name (str): _description_
            object_name (str): _description_

        Raises:
            Exception: _description_

        Returns:
            str: _description_
        """
        try:
            response = self.s3.generate_presigned_url(
                "put_object",
                Params={"Bucket": bucket_name, "Key": object_name},
                ExpiresIn=3600,
            )  # URL valid for 1 hour
            return response
        except ClientError as e:
            raise Exception(f"Failed to generate upload signed URL: {e}")

    def generate_download_signed_url(self, bucket_name: str, object_name: str) -> str:
        """Generate a signed URL for downloading a file.

        Args:
            bucket_name ): _description_
            object_name (str): _description_

        Raises:
            Exception: _description_

        Returns:
            str: _description_
        """
        try:
            response = self.s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": object_name},
                ExpiresIn=3600,
            )  # URL valid for 1 hour
            return response
        except ClientError as e:
            raise Exception(f"Failed to generate download signed URL: {e}")
