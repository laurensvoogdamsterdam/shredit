from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware

from api.db.pool import AsyncSessionLocal


# Middleware to attach the database session to the request state
class DbSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = None
        try:
            # Create a new AsyncSession
            request.state.db = AsyncSessionLocal()

            # Pass the request to the next middleware or route handler
            response = await call_next(request)

            # Commit the transaction if everything went well
            await request.state.db.commit()            

        except HTTPException as e:
            # Rollback in case of an error
            await request.state.db.rollback()
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

        except Exception as e:
            # Rollback in case of any other exception
            await request.state.db.rollback()
            return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

        finally:
            # Close the session after the request has been processed
            await request.state.db.close()

        return response
