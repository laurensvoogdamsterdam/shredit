import os

from cachetools import LRUCache, cached, TTLCache
from cachetools.keys import hashkey
from fastapi import BackgroundTasks, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.future import select
from starlette.middleware.base import BaseHTTPMiddleware

from api.db.models import User
from api.db.pool import AsyncSessionLocal
from api.utils.idp import IdentifyProviderFactory
from api.utils.logger import log
from sqlalchemy.orm import selectinload

from api.utils.logger import log

log = log.getChild(__name__)

# Set up a global LRU cache for Auth0 tokens with a max size of 1000 items
token_cache = TTLCache(maxsize=10000, ttl=3600)


# Middleware to attach user to request state
class Auth0Middleware(BaseHTTPMiddleware):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth = IdentifyProviderFactory.build()

    async def dispatch(self, request: Request, call_next):
        """Attach the user to the request state.

        Args:
            request (Request): _description_
            call_next (_type_): _description_

        Returns:
            _type_: _description_
        """
        try:
            # Get token from request
            token = await self.get_token_auth_header(request)
            token_in_cache = True if token in token_cache else False

            if not token_in_cache:
                token_validated = await self.auth.validate_token(token)
                user_info = await self.auth.get_user_info(token)
                cached_user = await self.get_or_create_user(user_info)
                token_cache[token] = cached_user
                request.state.user_info = cached_user
            else:
                cached_user = token_cache[token]
                request.state.user_info = cached_user

            response = await call_next(request)

        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
        return response

    async def get_token_auth_header(self, request: Request) -> str:
        """Obtain the access token from the Authorization header."""
        auth_header = request.headers.get("Authorization", None)
        if not auth_header:
            raise HTTPException(
                status_code=401, detail="Authorization header is expected"
            )
        parts = auth_header.split()
        if parts[0].lower() != "bearer":
            raise HTTPException(
                status_code=401, detail="Authorization header must start with Bearer"
            )
        elif len(parts) == 1:
            raise HTTPException(status_code=401, detail="Token not found")
        elif len(parts) > 2:
            raise HTTPException(
                status_code=401, detail="Authorization header must be Bearer token"
            )
        token = parts[1]
        return token

    async def get_or_create_user(self, user_info: dict):
        """Check if user exists in the database and insert if not."""
        async with AsyncSessionLocal() as session:
            # Example assumes your Auth0 user contains a 'sub' field for user ID
            auth_id = user_info["auth_id"]

            # Query the database to check if the user exists
            result = await session.execute(select(User).where(User.auth_id == auth_id))
            user = result.scalars().first()

            if not user:
                user = User(
                    auth_id=auth_id,
                    email=user_info["email"],
                    full_name=user_info["name"],
                    username=user_info["nickname"] if "nickname" in user_info else None,
                    avatar_url=user_info["picture"] if "picture" in user_info else None,
                    given_name=user_info["given_name"] if "given_name" in user_info else None,
                    family_name=user_info["family_name"]    if "family_name" in user_info else None,                    
                )
                session.add(user)
                await session.commit()

            # quer user including user.files, user.chat_rooms
            result = await session.execute(
                select(User)
                .where(User.auth_id == auth_id)
                .options(selectinload(User.files), selectinload(User.chat_rooms))
            )
            user = result.scalars().first()

        return user
