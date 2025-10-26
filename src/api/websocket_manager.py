"""
WebSocket connection manager.
Single Responsibility: Manage WebSocket connections and message handling.
Dependency Inversion: Depends on AuthenticationService abstraction.
"""
from typing import List, Dict, Any
from fastapi import WebSocket, WebSocketDisconnect
import json
from loguru import logger
from ..auth.auth_service import AuthenticationService


class WebSocketManager:
    """Manages WebSocket connections for real-time data streaming."""
    
    def __init__(self, auth_service: AuthenticationService):
        self.auth_service = auth_service
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    async def disconnect(self, websocket: WebSocket):
        """Disconnect a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
    
    async def broadcast(self, message: str):
        """Broadcast a message to all connected WebSocket clients."""
        for connection in self.active_connections.copy():
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Failed to broadcast to connection: {e}")
                self.active_connections.remove(connection)
    
    async def handle_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """Handle incoming WebSocket messages."""
        try:
            action = message.get("action")
            
            if action == "subscribe":
                await self.send_personal_message(json.dumps({
                    "type": "ack",
                    "message": "Subscribed successfully"
                }), websocket)
            
            elif action == "ping":
                await self.send_personal_message(json.dumps({
                    "type": "pong"
                }), websocket)
            
            else:
                await self.send_personal_message(json.dumps({
                    "type": "error",
                    "message": f"Unknown action: {action}"
                }), websocket)
                
        except Exception as e:
            logger.error(f"Failed to handle message: {e}")
            await self.send_personal_message(json.dumps({
                "type": "error",
                "message": str(e)
            }), websocket)
    
    async def handle_connection(self, websocket: WebSocket):
        """Handle a WebSocket connection lifecycle."""
        await self.connect(websocket)
        
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                await self.handle_message(websocket, message)
        
        except WebSocketDisconnect:
            await self.disconnect(websocket)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            await self.disconnect(websocket)
