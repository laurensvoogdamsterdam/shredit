import os
import api
from fastapi import FastAPI
import importlib
import pkgutil
from pathlib import Path
from api.utils.logger import log

class API(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_routers()

    def load_routers(self):
        """Dynamically load all routers from the api.router package."""
        routers_dir = Path(api.__file__).parent / "routers"
        # get all .py files in api.routers
        for f in os.listdir(Path(api.__file__).parent / "routers"):
            if f.endswith(".py") and not f.startswith("__"):
                # import the module
                module = importlib.import_module(f"api.routers.{f[:-3]}")
                if hasattr(module, "router"):
                    log.info(f"Loading router: {f}")    
                    self.include_router(module.router)
                
        
# Instantiate the API
api = API()
