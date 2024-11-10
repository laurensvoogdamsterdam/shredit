import os
from typing import Generator

from api.utils.logger import log

from .aws import ECSContainerPlatform
from .base import BaseContainerPlatform
from .docker import DockerPlatform


class ComputeFactory:
    @staticmethod
    def build() -> BaseContainerPlatform:
        platform = os.getenv("COMPUTE_PLATFORM", "docker")
        log.info(f"Building compute platform: {platform}")
        match platform:
            case "docker":
                return DockerPlatform()
            case "aws":
                return ECSContainerPlatform(region_name=os.getenv("AWS_REGION"))
            case _:
                raise ValueError(f"Invalid compute platform: {platform}")


def get_container_platform() -> BaseContainerPlatform:
    return ComputeFactory.build()
