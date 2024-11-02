from abc import ABC, abstractmethod
from typing import Any


class BaseContainerPlatform(ABC):
    """
    Abstract base class for managing workflow containers on a container platform.
    """

    @abstractmethod
    async def start_container(self, image: str, environment: dict[str, Any]) -> str:
        """Start a container for a workflow and return its unique container ID.

        Args:
            image (str): The container image to use.
            environment (dict): Environment variables for the container.

        Returns:
            str: The unique ID of the started container.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_container_status(self, container_id: str) -> str:
        """Get the current status of a container.

        Args:
            container_id (str): Unique ID of the container.

        Returns:
            str: The current status of the container (e.g., 'running', 'completed', 'failed').
        """
        raise NotImplementedError

    @abstractmethod
    async def stop_container(self, container_id: str) -> bool:
        """Stop a running container.

        Args:
            container_id (str): Unique ID of the container to stop.

        Returns:
            bool: True if the container was successfully stopped, False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_logs(self, container_id: str) -> str:
        """Retrieve logs for a specified container.

        Args:
            container_id (str): Unique ID of the container.

        Returns:
            str: Logs of the container.
        """
        raise NotImplementedError
