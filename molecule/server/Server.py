import uvicorn
import threading
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.logger import logger as fastapi_logger

from molecule.server.routes import router

class Server:
    def __init__(self):
        self.app = FastAPI()
        self.app.include_router(router)
        self.app.state.server = self
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:5173","http://localhost:5174"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Configure logging to suppress 200 responses
        logging.getLogger("uvicorn.access").addFilter(self.Suppress200Filter())

    class Suppress200Filter(logging.Filter):
        def filter(self, record):
            return "200 OK" not in record.getMessage()

    def start(self):
        # Configure uvicorn logging to suppress 200 responses
        access_log_config = logging.getLogger("uvicorn.access")
        access_log_config.addFilter(self.Suppress200Filter())

        server_thread = threading.Thread(
            target=uvicorn.run,
            args=(self.app,),
            kwargs={
                "host": "127.0.0.1",
                "port": 8000,
                "log_config": None,  # Disable default uvicorn logging
            },
        )
        server_thread.start()

    def switch_level(self, level):
        self.level = level