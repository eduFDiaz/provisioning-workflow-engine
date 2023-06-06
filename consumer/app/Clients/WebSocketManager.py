import asyncio
from typing import Dict
from fastapi import WebSocket
from fastapi.websockets import WebSocketState, WebSocketDisconnect
from config import logger as log

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    async def disconnect(self, client_id: str):
        await self.active_connections[client_id].close()
        del self.active_connections[client_id]

    async def send_message(self, client_id: str, message: str):
        log.info(f"WebSocketManager.send_message() - client_id: {client_id} - message: {message}")
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(message)
            except WebSocketDisconnect:
                await self.disconnect(client_id)

    async def keep_alive(self, client_id: str, timeout: float = 10.0):
        while True:
            try:
                if self.active_connections[client_id].application_state == WebSocketState.DISCONNECTED:
                    del self.active_connections[client_id]
                    break
                else:
                    await self.active_connections[client_id].send_text('ping')
            except Exception as e:
                print(e)
            await asyncio.sleep(timeout)

    def get_manager(self):
        return self