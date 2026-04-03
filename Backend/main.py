import logging
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from core.websocket_manager import ws_manager
from features.api import router as api_router
import time
import asyncio

# Ensure logs directory exists with absolute path
LOG_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Configure Logging
logger = logging.getLogger("hacker-society")
logger.setLevel(logging.INFO)

# Create file handler
fh = logging.FileHandler(LOG_FILE)
fh.setLevel(logging.INFO)

# Create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# Add handlers
logger.addHandler(fh)
logger.addHandler(ch)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Kicks off the background heartbeat loop for WebSockets during startup.
    """
    logger.info("Starting WebSocket heartbeat background task...")
    asyncio.create_task(ws_manager.start_heartbeat())
    yield
    # Cleanup logic (if any) goes here after yield

app = FastAPI(
    title="Hacker Society API", 
    description="Mission Control for CAMEL Agents",
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
    return {"status": "Hacker Society Operations Active"}

app.include_router(api_router, prefix="/api")

@app.websocket("/ws/events")
async def websocket_events(websocket: WebSocket):
    """
    The singular, multiplexed WebSocket connecting the React Frontend 
    to the autonomous operations.
    """
    origin = websocket.headers.get("origin")
    logger.info(f"Incoming WebSocket connection attempt from origin: {origin}")
    
    await ws_manager.connect(websocket)
    await ws_manager.broadcast_json("system", {"message": "Glass Box WebSocket connected!"})
    
    try:
        while True:
            # Keep connection alive, though we only push unidirectionally downstream
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
