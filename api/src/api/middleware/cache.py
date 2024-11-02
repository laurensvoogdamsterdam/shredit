import hashlib
import json

from cachetools import LRUCache
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from api.utils.logger import log

# Set up a global LRU cache with a max size of 1000 items
response_cache = LRUCache(maxsize=10000)

cache_paths = [
    "/users/me",
]


class ResponseCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.headers.get("Authorization")
        cache_key = self.generate_cache_key(token, request.url.path)

        #  check if request path is in cache_paths
        if request.url.path in cache_paths:
            cached_response = response_cache.get(cache_key)
            if cached_response:
                # If the response is cached, return it
                return JSONResponse(
                    status_code=201,
                    content=json.loads(cached_response["content"]),
                )

        # Call the next middleware or endpoint
        response = await call_next(request)

        if request.url.path in cache_paths and response.status_code == 200:
            body = [content async for content in response.body_iterator]
            response.__setattr__("body_iterator", AsyncIteratorWrapper(body))
            try:
                body = json.loads(b"".join(body))
                #  set ru cacche for key
                response_cache[cache_key] = {
                    "status_code": response.status_code,
                    "content": json.dumps(body),
                }
            except Exception as e:
                log.error("Failed to cache response", e)

        return response

    def generate_cache_key(self, token: str, path: str) -> str:
        """Generate a unique cache key based on the access token and path."""
        token_hash = (
            hashlib.sha256(token.encode()).hexdigest() if token else "anonymous"
        )
        return f"{path}_{token_hash}"

    def invalidate_cache(self, token: str, path: str):
        """Invalidate cache entries for the specified token."""
        # Invalidate cache for the /users/me endpoint
        cache_key = self.generate_cache_key(token, path)
        response_cache.pop(cache_key, None)


class AsyncIteratorWrapper:
    def __init__(self, obj):
        self._it = iter(obj)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            value = next(self._it)
        except StopIteration:
            raise StopAsyncIteration
        return value
