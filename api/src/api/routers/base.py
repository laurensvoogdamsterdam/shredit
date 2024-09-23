
from fastapi import APIRouter

router = APIRouter(
    prefix="/base",
    tags=["base"],
    responses={404: {"description": "Not found"}},
)


router.get("/")(lambda: {"message": "Hello World!"})
async def hello_world():    
    return {"message": "Hello World!"}