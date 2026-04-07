import json
import asyncio
import time
import logging
from typing import List, Optional
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger("hacker-society")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.main_loop: Optional[asyncio.AbstractEventLoop] = None

    def set_loop(self, loop: asyncio.AbstractEventLoop):
        """
        Anchors the manager to the main thread's event loop.
        """
        self.main_loop = loop
        logger.info("[WS] Manager anchored to main loop.")

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"[WS] Client connected. Active count: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"[WS] Client disconnected. Active count: {len(self.active_connections)}")

    async def broadcast_json(self, stream_type: str, data: dict):
        payload = { "type": stream_type, "data": data }
        json_payload = json.dumps(payload)
        
        dead_sockets = []
        for connection in self.active_connections:
            try:
                # State 1 is CONNECTED
                if connection.client_state.value == 1:
                    await connection.send_text(json_payload)
                else:
                    dead_sockets.append(connection)
            except (RuntimeError, WebSocketDisconnect, ConnectionError):
                dead_sockets.append(connection)
            except Exception as e:
                logger.error(f"[WS] Broadcast error: {e}")
        
        for dead in dead_sockets:
            self.disconnect(dead)

    def emit(self, stream_type: str, data: dict):
        """
        Thread-safe broadcast entrypoint for agent worker threads.
        """
        if not self.main_loop:
            logger.warning("[WS] Emit attempted before loop was set.")
            return
            
        asyncio.run_coroutine_threadsafe(
            self.broadcast_json(stream_type, data),
            self.main_loop
        )

    async def start_heartbeat(self):
        while True:
            await asyncio.sleep(30)
            if self.active_connections:
                await self.broadcast_json("system", {"message": "heartbeat", "timestamp": time.time()})

ws_manager = ConnectionManager()
