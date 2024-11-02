from abc import ABC, abstractmethod
from typing import Union


class BaseStorage(ABC):
    """Abstract base class for managing storage operations."""

    @abstractmethod
    def delete_file(self, bucket_name: str, object_name: str) -> None:
        """Delete a file from the specified bucket

        Args:
            bucket_name (str): _description_
            object_name (str): _description_

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError

    @abstractmethod
    async def generate_upload_signed_url(
        self, bucket_name: str, object_name: str
    ) -> str:
        """Generate a signed URL for uploading a file.

        Args:
            bucket_name (str): _description_
            object_name (str): _description_

        Raises:
            NotImplementedError: _description_

        Returns:
            str: _description_
        """
        raise NotImplementedError

    @abstractmethod
    async def generate_download_signed_url(
        self, bucket_name: str, object_name: str
    ) -> str:
        """Generate a signed URL for downloading a file.

        Args:
            bucket_name (str): _description_
            object_name (str): _description_

        Raises:
            NotImplementedError: _description_

        Returns:
            str: _description_
        """
        raise NotImplementedError
