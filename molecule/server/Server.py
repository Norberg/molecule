import uvicorn
import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from molecule.server.routes import router

class Server:
    def __init__(self):
        self.app = FastAPI()
        self.app.include_router(router)
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:5173","http://localhost:5174"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def start(self):
        server_thread = threading.Thread(target=uvicorn.run, args=(self.app,), kwargs={"host": "127.0.0.1", "port": 8000})
        server_thread.start()