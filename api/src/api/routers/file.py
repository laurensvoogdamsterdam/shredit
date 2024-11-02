import os
from datetime import timedelta
from typing import Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from google.cloud import storage
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from api.db.models import File as FileModel
from api.db.models import User
from api.db.pool import get_db
from api.utils.blob import BaseStorage, BlobFactory, get_blob_storage
from api.utils.logger import log

storage: BaseStorage = get_blob_storage()


# Define the FastAPI router
router = APIRouter(prefix="/files", tags=["files"])


# Define Pydantic models
class FileMetadata(BaseModel):
    id: int
    file_url: str
    file_name: str
    content_type: str
    uploaded_at: str


class FileUploadRequest(BaseModel):
    file_name: str
    content_type: str
    operation: Optional[str] = "upload"


class FileUpdateRequest(BaseModel):
    new_file_name: str
    content_type: str


class FileResponse(BaseModel):
    file_url: str
    signed_url: Optional[str] = None


class FileDeletedResponse(BaseModel):
    message: str


@router.post("/signedurl", response_model=FileResponse)
async def generate_presigned_url(
    file_request: FileUploadRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    storage: BaseStorage = Depends(get_blob_storage),
):
    """Generate a signed URL for file upload, update, or deletion.

    Args:
        request (Request): Request object with user's auth0_id
        file_request (FileUploadRequest): File metadata
        operation (str): Operation type: upload, update, or delete
        db (AsyncSession, optional): Db conn. Defaults to Depends(get_db).
        storage (BaseStorage, optional): Blob storage. Defaults to Depends(get_blob_storage).

    Raises:
        HTTPException: _description_

    Returns:
        FileResponse: File URL and signed URL
    """
    # check if operations  is allowed
    if file_request.operation not in ["upload", "update", "delete"]:
        raise HTTPException(status_code=400, detail="Invalid operation type")

    # Get the user from the request state
    user = request.state.user_info

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Generate a signed URL for file upload
    file_name = file_request.file_name
    content_type = file_request.content_type
    file_path = f"user_{user.id}/{file_name}"
    signed_url = storage.generate_upload_signed_url(
        "users",
        file_path,
    )

    # Save the file metadata to the database
    if file_request.operation == "upload":
        file_record = FileModel(
            user=user,
            file_name=file_name,
            content_type=content_type,
            file_url=file_path,
        )
        db.add(file_record)
        await db.commit()

    return FileResponse(file_url=file_path, signed_url=signed_url)


@router.delete("/{file_id}", response_model=FileDeletedResponse)
async def delete_file(
    file_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    storage: BaseStorage = Depends(get_blob_storage),
):
    """Delete a file from GCS and the database.

    Args:
        file_id (int): ID of existing file to delete
        request (Request): Request object with user's auth0_id
        db (AsyncSession, optional): Db connection. Defaults to Depends(get_db).

    Raises:
        HTTPException: _description_

    Returns:
        FileDeletedResponse: File deleted status response
    """
    # Get the user from the request state
    user = request.state.user_info
    if user is None:
        return HTTPException(status_code=404, detail="User not found")

    # get file from user.files where file_id = file.id
    file_record = next((file for file in user.files if file.id == file_id), None)
    if file_record is None:
        return FileDeletedResponse(message="File not found")

    # remove file from storage
    background_tasks.add_task(storage.delete_file, "users", file_record.file_url)

    # Remove file metadata from database
    await db.delete(file_record)
    await db.commit()

    return FileDeletedResponse(message="File deleted successfully")


@router.get("/", response_model=list[FileMetadata])
async def list_files(
    request: Request,
    db: AsyncSession = Depends(get_db),
    storage: BaseStorage = Depends(get_blob_storage),
):
    """List all files for the current user."""
    # Get the user from the request
    user = request.state.user_info
    if user is None:
        return []  # or raise HTTPException if you prefer

    # Prepare the file metadata with signed URLs
    file_metadata_with_urls = []
    for file in user.files:  # Access files through the user object
        signed_url = storage.generate_download_signed_url("users", file.file_url)
        file_metadata_with_urls.append(
            FileMetadata(
                id=file.id,
                file_url=signed_url,  # Use signed URL here
                file_name=file.file_name,
                content_type=file.content_type,
                uploaded_at=str(file.uploaded_at),
            )
        )

    return file_metadata_with_urls
