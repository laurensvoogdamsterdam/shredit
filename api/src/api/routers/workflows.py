import json
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from api.db.models import WorkflowStatus, Workflow, WorkflowInstance
from api.db.models import File as FileModel
from api.db.models import Message, MessageType, User, chat_members
from api.db.pool import get_db
from api.utils.compute import get_container_platform, BaseContainerPlatform


router = APIRouter(prefix="/workflows", tags=["chat"])


# Models for request and response
class WorkflowStartResponse(BaseModel):
    workflow_id: str
    status: str


class WorkflowStatusResponse(BaseModel):
    workflow_id: str
    status: str
    results: Optional[dict] = None


class WorkflowResponse(BaseModel):
    id: int
    status: str
    container_id: str


class WorkflowInstanceLogs(BaseModel):
    message: str


class WorkflowStoppingResponse(BaseModel):
    message: str


class WorkflowResponse(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        orm_mode = True


@router.post("/start", response_model=WorkflowResponse)
async def start_workflow(
    workflow_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    container_platform: BaseContainerPlatform = Depends(get_container_platform),
):
    """Start a new workflow instance.

    Args:
        workflow_id (int): _description_
        request (Request): _description_
        db (AsyncSession, optional): _description_. Defaults to Depends(get_db).
        container_platform (BaseContainerPlatform, optional): _description_. Defaults to Depends(get_container_platform).

    Raises:
        HTTPException: _description_
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    # Get the user ID from the request state
    user = request.state.user_info["auth_id"]
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Retrieve the workflow details from DB
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalars().first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Start a container for the workflow using the specified container platform
    try:
        container_id = await container_platform.start_container(
            image=workflow.name,  # Assuming the workflow name matches the container image
            environment={},  # Set any required environment variables
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to start workflow container: {e}"
        )

    # Log the workflow instance in DB
    instance = WorkflowInstance(
        workflow_id=workflow_id,
        user_id=user.id,
        status=WorkflowStatus.RUNNING,
        started_at=datetime.utcnow(),
        container_id=container_id,
    )
    db.add(instance)
    db.commit()

    return WorkflowResponse(
        id=instance.id, status=instance.status, container_id=container_id
    )


@router.get("/status/{instance_id}", response_model=WorkflowStatusResponse)
async def get_workflow_status(
    instance_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    container_platform: BaseContainerPlatform = Depends(get_container_platform),
):
    """Get the status of a workflow instance.

    Args:
        instance_id (int): _description_
        request (Request): _description_
        db (AsyncSession, optional): _description_. Defaults to Depends(get_db).
        container_platform (BaseContainerPlatform, optional): _description_. Defaults to Depends(get_container_platform).

    Raises:
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    # get user
    user = request.state.user_info["auth_id"]
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get the workflow instance from DB
    result = await db.execute(
        select(WorkflowInstance).where(WorkflowInstance.id == instance_id)
    )
    instance = result.scalars().first()
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow instance not found")

    # Get the container status from the container platform
    try:
        status = await container_platform.get_container_status(instance.container_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve container status: {e}"
        )

    # Update the status in DB if changed
    if status != instance.status:
        instance.status = status
        if status == WorkflowStatus.COMPLETED:
            instance.completed_at = datetime.utcnow()
        db.commit()

    return WorkflowStatusResponse(id=instance.id, status=instance.status)


@router.post("/stop/{instance_id}")
async def stop_workflow(
    instance_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    container_platform: BaseContainerPlatform = Depends(get_container_platform),
):
    """Stop a running workflow instance.

    Args:
        instance_id (int): _description_
        request (Request): _description_
        db (AsyncSession, optional): _description_. Defaults to Depends(get_db).
        container_platform (BaseContainerPlatform, optional): _description_. Defaults to Depends(get_container_platform).

    Raises:
        HTTPException: _description_
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    user = request.state.user_info["auth_id"]
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # check if user is owner of instance
    result = await db.execute(
        select(WorkflowInstance).where(WorkflowInstance.id == instance_id)
    )
    instance = result.scalars().first()
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow instance not found")

    if instance.user_id != user.id:
        raise HTTPException(
            status_code=403, detail="User not authorized to stop this workflow"
        )

    # Stop the container
    try:
        stopped = await container_platform.stop_container(instance.container_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop container: {e}")

    if stopped:
        instance.status = WorkflowStatus.FAILED
        db.commit()

    return WorkflowStoppingResponse(message="Workflow stopped")


@router.get("/logs/{instance_id}")
async def get_workflow_logs(
    instance_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    container_platform: BaseContainerPlatform = Depends(get_container_platform),
):
    """Get the logs of a workflow instance.

    Args:
        instance_id (int): _description_
        request (Request): _description_
        db (AsyncSession, optional): _description_. Defaults to Depends(get_db).
        container_platform (BaseContainerPlatform, optional): _description_. Defaults to Depends(get_container_platform).

    Raises:
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    user = request.state.user_info["auth_id"]
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = db.execute(
        select(WorkflowInstance).where(WorkflowInstance.id == instance_id)
    )
    instance = result.scalars().first()
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow instance not found")

    try:
        logs = await container_platform.get_logs(instance.container_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve logs: {e}")

    return WorkflowInstanceLogs(message=logs)


#  get workflows endpoint
@router.get("/", response_model=List[WorkflowResponse])
async def get_workflows(
    db: AsyncSession = Depends(get_db),
):
    """Get a list of all available workflows.

    Args:
        db (AsyncSession, optional): _description_. Defaults to Depends(get_db).

    Returns:
        List[Workflow]: _description_
    """
    result = await db.execute(select(Workflow))
    workflows = result.scalars().all()
    return workflows
