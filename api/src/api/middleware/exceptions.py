from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from api.utils.logger import log

# Initialize logging


class HTTPExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            # Handle HTTPException cases specifically
            if response.status_code >= 400:
                log.error(f"HTTPException: {response.status_code}")
            return response

        # Handle FastAPI HTTPExceptions explicitly
        except HTTPException as exc:
            log.error(f"HTTPException: {exc.detail}")
            return JSONResponse(
                status_code=exc.status_code,
                content={"error": exc.detail, "status_code": exc.status_code},
            )

        # Handle generic Python exceptions
        except Exception as exc:
            log.exception("Unhandled Exception")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "An internal server error occurred",
                    "status_code": 500,
                },
            )
