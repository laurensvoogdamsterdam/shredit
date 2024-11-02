from typing import Any

import docker
from docker.models.containers import Container

from .base import BaseContainerPlatform


class DockerPlatform(BaseContainerPlatform):
    """Docker platform to manage containers."""

    def __init__(self):
        self.client = docker.from_env()

    async def start_container(self, image: str, environment: dict[str, Any]) -> str:
        """Start a container with the specified image and environment variables.

        Args:
            image (str): _description_
            environment (dict[str, Any]): _description_

        Returns:
            str: _description_
        """
        container = self.client.containers.run(
            image, detach=True, environment=environment
        )
        return container.id

    async def get_container_status(self, container_id: str) -> str:
        """Get the status of the container.

        Args:
            container_id (str): _description_

        Returns:
            str: _description_
        """
        container = self.client.containers.get(container_id)
        return container.status

    async def stop_container(self, container_id: str) -> bool:
        """Stop the container.

        Args:
            container_id (str): _description_

        Returns:
            bool: _description_
        """
        container = self.client.containers.get(container_id)
        container.stop()
        return container.status == "exited"

    async def get_logs(self, container_id: str) -> str:
        """Get the logs of the container.

        Args:
            container_id (str): _description_

        Returns:
            str: _description_
        """
        container = self.client.containers.get(container_id)
        return container.logs().decode("utf-8")
