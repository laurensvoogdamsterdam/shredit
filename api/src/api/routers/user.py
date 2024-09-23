from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from api.db.pool import get_db
import api.db.models as models

router = APIRouter(
    prefix="/users",
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic models
class User(BaseModel):
    id: str
    email: str
    name: str

class UpdateUser(BaseModel):
    name: str

# Dependency to get the current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Here you would validate the token with Auth0 and decode it
    # This is a placeholder for demonstration
    user_info = {
        "id": "123",
        "email": "user@example.com",
        "name": "User Name"
    }
    return User(**user_info)

@router.get("/me", response_model=User)
async def read_user(current_user: User = Depends(get_current_user)):
    return current_user

#  get all users from db
@router.get("/all")
async def get_users(db:AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User))
    users = result.scalars().all()  # Use .scalars() to unpack result
    return users