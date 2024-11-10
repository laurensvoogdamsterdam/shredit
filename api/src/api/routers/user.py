from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

# from sqlalchemy.future import select
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

import api.db.models as models
from api.db.pool import get_db
from api.utils.logger import log

router = APIRouter(
    prefix="/users",
)


class User(BaseModel):
    id: int
    email: str
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None

    class Config:
        from_attributes = True


class UpdateUser(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None


@router.get("/me", response_model=User)
async def read_user(request: Request, db: AsyncSession = Depends(get_db)):
    """Get the current user from the database.

    Args:
        request (Request): _description_. Request object from which when logged i contains the auth0_id
        db (AsyncSession, optional): _description_. Defaults to Depends(get_db).

    Raises:
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    user = request.state.user_info
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    # print al fields from user
    print(user.asdict())
    return User(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        username=user.username,
        role=user.role.value,
    )


# Update authenticated user's profile
@router.put("/me", response_model=User)
async def update_user(
    request: Request, update_data: UpdateUser, db: AsyncSession = Depends(get_db)
):
    """Update the authenticated user's profile

    Args:
        request (Request): The request object with the user's auth0_id
        update_data (UpdateUser): The data to update the user with
        db (AsyncSession, optional): Db connecton. Defaults to Depends(get_db).

    Raises:
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    user = request.state.user_info
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Update only fields that are provided
    if update_data.name:
        user.full_name = update_data.name
    if update_data.email:
        user.email = update_data.email
    if update_data.role:
        user.role = update_data.role

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return User(
        id=user.id, email=user.email, full_name=user.full_name, role=user.role.value
    )


# Delete the authenticated user
@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(request: Request, db: AsyncSession = Depends(get_db)):
    """Delete the authenticated user.

    Args:
        request (Request):  The request object with the user's auth0_id
        db (AsyncSession, optional): Db connection. Defaults to Depends(get_db).

    Raises:
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    user = request.state.user_info
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    await db.delete(user)
    await db.commit()
    return {"message": "User deleted successfully"}


#  method to search a user
@router.get("/search", response_model=List[User])
async def search_user_by_query(query: str, db: AsyncSession = Depends(get_db)):
    """Search a user by ID.

    Args:
        id (int): The ID of the user to search for
        db (AsyncSession, optional): Db connection. Defaults to Depends(get_db).

    Raises:
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    # remove starting and trailding whitespaces from query
    query = query.strip()
    if not query:
        return []
    #  create stmnt to fzzy search username (lowercase)
    stmt = (
        select(models.User)
        .where(
            or_(
                models.User.username.ilike(f"%{query}%"),
                models.User.full_name.ilike(f"%{query}%"),
                models.User.email.ilike(f"%{query}%"),
            )
        )
        .order_by(models.User.username)
        .limit(10)
    )

    result = await db.execute(stmt)
    users = result.scalars().all()

    return [
        User(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            username=user.username,
            avatar_url=user.avatar_url,
        )
        for user in users
    ]


#  get all users from db
@router.get("/all", response_model=List[User])
async def get_users(db: AsyncSession = Depends(get_db)):
    """Get all users from the database.

    Args:
        db (AsyncSession, optional): _description_. Defaults to Depends(get_db).

    Returns:
        List[User]: _description_. List of users
    """

    result = await db.execute(select(models.User))
    users = result.scalars().all()
    return users
