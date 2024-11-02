import os

from .aws import S3Storage
from .azure import AzureBlob
from .base import BaseStorage
from .gcp import GCPStorage


#  create BlobFactory to get instance of base dependent if you use gcp, aws or azure
class BlobFactory:

    @staticmethod
    def build() -> BaseStorage:
        """Build the blob storage instance

        Raises:
            ValueError: _description_

        Returns:
            BaseStorage: _description_
        """
        provider = os.getenv("BLOB_PROVIDER", "aws")
        match provider:
            case "aws":
                return S3Storage()
            case "gcp":
                return GCPStorage()
            case "azure":
                return AzureBlob()
            case _:
                raise ValueError(f"Invalid BLOB_PROVIDER: {provider}")


def get_blob_storage() -> BaseStorage:
    """Get the blob storage instance

    Returns:
        BaseStorage: _description_

    Yields:
        Iterator[BaseStorage]: _description_
    """
    yield BlobFactory.build()
