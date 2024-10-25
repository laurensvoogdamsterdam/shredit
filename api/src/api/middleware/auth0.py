from fastapi import BackgroundTasks, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.future import select
from starlette.middleware.base import BaseHTTPMiddleware

from api.db.models import User
from api.db.pool import AsyncSessionLocal
from api.utils.auth0 import get_current_user, get_token_auth_header, get_user_info
from api.utils.logger import log


# Middleware to attach user to request state
class Auth0Middleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            token = await get_token_auth_header(request)
            auth0_user = await get_current_user(token)
            request.state.user_auth0_id = auth0_user
            tasks = BackgroundTasks()
            tasks.add_task(self.check_and_insert_user, auth0_user, token)   
            response = await call_next(request)
            response.background = tasks
                    

        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
        return response

    async def check_and_insert_user(self, auth0_user: dict,token: str): 
        """Check if user exists in the database and insert if not."""
        async with AsyncSessionLocal() as session:
            # Example assumes your Auth0 user contains a 'sub' field for user ID
            user_id = auth0_user["sub"]

            # Query the database to check if the user exists
            result = await session.execute(select(User).where(User.auth0_id == user_id))
            user = result.scalars().first()
            # If the user doesn't exist, create a new user record
            if not user:
                user_info = get_user_info(token)
                new_user = User(auth0_id=user_id, email=user_info["email"], full_name=user_info["name"])
                session.add(new_user)
                await session.commit()
            

            

                