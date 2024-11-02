import os
from typing import Generator
from .base import BaseContainerPlatform
from .docker import DockerPlatform
from .aws import ECSContainerPlatform


class ComputeFactory:
    @staticmethod
    def build() -> BaseContainerPlatform:
        platform = os.getenv("COMPUTE_PLATFORM", "docker")
        match platform:
            case "docker":
                return DockerPlatform()
            case "aws":
                return ECSContainerPlatform(region_name=os.getenv("AWS_REGION"))
            case _:
                raise ValueError(f"Invalid compute platform: {platform}")


def get_container_platform(r) -> Generator[BaseContainerPlatform, None, None]:
    yield ComputeFactory.build()
