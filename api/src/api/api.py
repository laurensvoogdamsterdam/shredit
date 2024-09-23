import os
import api
from fastapi import FastAPI
import importlib
import pkgutil
from pathlib import Path
from api.utils.logger import log
from api.db.pool import init_db
import asyncio
from strawberry.fastapi import GraphQLRouter
from api.db.pool import AsyncSessionLocal
from api.utils.gql import schema

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

        # include gql routers
        self.include_router(GraphQLRouter(schema), prefix="/gql")
                
        
# Instantiate the API
app = API()

# Use FastAPI's startup event to initialize
@app.on_event("startup")
async def startup_event():
    await app.init()


@app.middleware("http")
async def add_session_to_context(request, call_next):
    response = await call_next(request)
    response.state.session = AsyncSessionLocal()
    return response
