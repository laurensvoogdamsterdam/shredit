from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(
    prefix="/base",
    tags=["base"],
    responses={404: {"description": "Not found"}},
)


router.get("/")(lambda: {"message": "Hello World!"})


class AliveResponse(BaseModel):
    message: str


@router.get("/", response_model=AliveResponse)
async def hello_world():
    """Check if the API is running.

    Returns:
        _type_: _description_
    """
    return AliveResponse(message="Running!")
