import asyncio
import importlib
import os
import pkgutil
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette_graphene3 import GraphQLApp, make_playground_handler
from strawberry.fastapi import GraphQLRouter

import api
from api.db.pool import AsyncSessionLocal, get_db, init_db
from api.middleware import (
    Auth0Middleware,
    HTTPExceptionMiddleware,
    ResponseCacheMiddleware,
)
from api.utils.gql import schema
from api.utils.logger import log


class API(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def init(self) -> None:
        # setup db
        await init_db()

        # include routers
        routers_dir = Path(api.__file__).parent / "routers"
        # get all .py files in api.routers
        for f in os.listdir(Path(api.__file__).parent / "routers"):
            if f.endswith(".py") and not f.startswith("__"):
                # import the module
                module = importlib.import_module(f"api.routers.{f[:-3]}")
                if hasattr(module, "router"):
                    log.info(f"Loading router: {f}")
                    self.include_router(module.router)

        # include gql router
        self.add_route("/gql", GraphQLApp(schema, on_get=make_playground_handler()))


# Instantiate the API
app = API()


# Use FastAPI's startup event to initialize
@app.on_event("startup")
async def startup_event():
    await app.init()


# cors middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow your Next.js app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type", "Access-Control-Allow-Origin"],
)

# middleware for auth0
app.add_middleware(Auth0Middleware)
app.add_middleware(ResponseCacheMiddleware)
app.add_middleware(HTTPExceptionMiddleware)
