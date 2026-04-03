import json
import asyncio
import time
from typing import List
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_json(self, stream_type: str, data: dict):
        # We multiplex payload types dynamically onto the same socket.
        payload = {
            "type": stream_type,
            "data": data
        }
        json_payload = json.dumps(payload)
        
        # Capture disconnected sockets first to avoid mutation during iteration
        disconnected_sockets = []
        
        for connection in self.active_connections:
            # Check starlette states: CONNECTED=1, DISCONNECTED=3
            # We skip anything that isn't actively connected to avoid "Cannot call send" errors.
            try:
                if connection.client_state.value != 1:
                    disconnected_sockets.append(connection)
                    continue
            except AttributeError:
                # If state isn't available, try to send and catch failure
                pass
                
            try:
                await connection.send_text(json_payload)
            except (RuntimeError, WebSocketDisconnect) as e:
                disconnected_sockets.append(connection)
            except Exception as e:
                print(f"Unexpected error in broadcast: {e}")

        # Cleanup dead connections
        for dead_ws in disconnected_sockets:
            self.disconnect(dead_ws)

    async def start_heartbeat(self):
        """
        Emits a periodic 'ping' to all active connections to help with 
        network debugging and keep-alive.
        """
        while True:
            await asyncio.sleep(30)
            if self.active_connections:
                await self.broadcast_json("system", {"message": "heartbeat", "timestamp": time.time()})

ws_manager = ConnectionManager()
