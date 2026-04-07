import logging
import os
import asyncio
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.websocket_manager import ws_manager
from features.api import router as api_router

# Ensure logs directory exists
LOG_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Configure Logging
logger = logging.getLogger("hacker-society")
logger.setLevel(logging.INFO)

fh = logging.FileHandler(LOG_FILE)
fh.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Kicks off core mission-critical background services on startup.
    Anchors the WebSocket manager to the master event loop for cross-thread emission.
    """
    loop = asyncio.get_running_loop()
    ws_manager.set_loop(loop)
    
    logger.info("Initializing WebSocket heartbeat background task...")
    asyncio.create_task(ws_manager.start_heartbeat())
    yield
    # Cleanup logic (if any) goes here

app = FastAPI(
    title="Autonomous Security Workforce API", 
    description="Mission Control for CAMEL-powered Security Orchestration",
    lifespan=lifespan
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"Method: {request.method} Path: {request.url.path} Status: {response.status_code} Duration: {duration:.2f}s")
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "Autonomous Security Workforce Operations Active"}

app.include_router(api_router, prefix="/api")

@app.websocket("/ws/events")
async def websocket_events(websocket: WebSocket):
    """
    Multiplexed dashboard stream for neural feeds and terminal traces.
    """
    try:
        # 1. Establish and accept connection
        await ws_manager.connect(websocket)
        await ws_manager.broadcast_json("system", {"message": "Neural stream established!"})
        
        # 2. Keep connection alive
        while True:
            # Maintain active connection
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket execution error: {str(e)}")
        ws_manager.disconnect(websocket)
