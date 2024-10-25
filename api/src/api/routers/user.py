from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import api.db.models as models
from api.db.pool import get_db
from api.utils.logger import log

router = APIRouter(
    prefix="/users",
)

# Pydantic models
class User(BaseModel):
    id: int
    email: str
    name: str

class UpdateUser(BaseModel):
    name: str


@router.get("/me", response_model=User)
async def read_user(request: Request, db: AsyncSession = Depends(get_db)):
    auth0_id = request.state.user_auth0_id.get("sub") 
    #  get user where auth0_id = auth0_id
    result = await db.execute(select(models.User).where(models.User.auth0_id == auth0_id))
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return User(id=user.id, email=user.email, name=user.full_name)

#  get all users from db
@router.get("/all")
async def get_users(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User))
    users = result.scalars().all()  
    return users