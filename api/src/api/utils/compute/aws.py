from typing import Any, Dict

import aioboto3

from .base import BaseContainerPlatform


class ECSContainerPlatform(BaseContainerPlatform):
    def __init__(self, region_name: str):
        self.region_name = region_name

    async def start_container(
        self,
        image: str,
        environment: Dict[str, Any],
        task_definition: str,
        cluster: str = "default",
    ) -> str:
        """Start a container for a workflow and return its unique task ARN."""
        async with aioboto3.client("ecs", region_name=self.region_name) as ecs_client:
            response = await ecs_client.run_task(
                cluster=cluster,
                taskDefinition=task_definition,
                overrides={
                    "containerOverrides": [
                        {
                            "name": task_definition,
                            "environment": [
                                {"name": key, "value": str(value)}
                                for key, value in environment.items()
                            ],
                        },
                    ],
                },
                launchType="FARGATE",  # Change this if using EC2 launch type
                networkConfiguration={
                    "awsvpcConfiguration": {
                        "subnets": ["your-subnet-id"],  # Replace with your subnet IDs
                        "assignPublicIp": "ENABLED",  # or 'DISABLED'
                    }
                },
            )
            task_arn = response["tasks"][0]["taskArn"]
            return task_arn

    async def get_container_status(self, task_arn: str) -> str:
        """Get the current status of a container."""
        async with aioboto3.client("ecs", region_name=self.region_name) as ecs_client:
            response = await ecs_client.describe_tasks(
                tasks=[task_arn], cluster="default"  # Specify your cluster name
            )
            task_status = response["tasks"][0]["lastStatus"]
            return task_status

    async def stop_container(self, task_arn: str) -> bool:
        """Stop a running container."""
        async with aioboto3.client("ecs", region_name=self.region_name) as ecs_client:
            response = await ecs_client.stop_task(
                task=task_arn, cluster="default"  # Specify your cluster name
            )
            return response["task"]["stoppedReason"] is not None

    async def get_logs(self, task_arn: str) -> str:
        """Retrieve logs for a specified container."""
        async with aioboto3.client("logs", region_name=self.region_name) as logs_client:
            # Extract the task ID from the ARN
            task_id = task_arn.split("/")[-1]
            log_group_name = f"/ecs/{task_id}"  # Customize if needed
            response = await logs_client.get_log_events(
                logGroupName=log_group_name, logStreamName=task_id, startFromHead=True
            )
            logs = [event["message"] for event in response["events"]]
            return "\n".join(logs)
