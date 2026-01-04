"""WebSocket connection manager."""
from typing import List, Set
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.client_data: dict = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Register a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.client_data[client_id] = {
            "websocket": websocket,
            "subscriptions": set()
        }
        logger.info(f"Client {client_id} connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, client_id: str):
        """Unregister a WebSocket connection."""
        if client_id in self.client_data:
            ws = self.client_data[client_id]["websocket"]
            if ws in self.active_connections:
                self.active_connections.remove(ws)
            del self.client_data[client_id]
            logger.info(f"Client {client_id} disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict, exclude: str = None):
        """Send message to all connected clients."""
        disconnected = []
        for client_id, client_info in self.client_data.items():
            if exclude and client_id == exclude:
                continue
            
            try:
                await client_info["websocket"].send_json(message)
            except Exception as e:
                logger.error(f"Error sending to {client_id}: {e}")
                disconnected.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id)
    
    async def broadcast_to_subscriptions(self, event_type: str, data: dict):
        """Send message to clients subscribed to event type."""
        message = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        disconnected = []
        for client_id, client_info in self.client_data.items():
            if event_type in client_info["subscriptions"]:
                try:
                    await client_info["websocket"].send_json(message)
                except Exception as e:
                    logger.error(f"Error sending to {client_id}: {e}")
                    disconnected.append(client_id)
        
        for client_id in disconnected:
            self.disconnect(client_id)
    
    def subscribe(self, client_id: str, event_type: str):
        """Subscribe a client to an event type."""
        if client_id in self.client_data:
            self.client_data[client_id]["subscriptions"].add(event_type)
    
    def unsubscribe(self, client_id: str, event_type: str):
        """Unsubscribe a client from an event type."""
        if client_id in self.client_data:
            self.client_data[client_id]["subscriptions"].discard(event_type)


# Global connection manager instance
manager = ConnectionManager()


from datetime import datetime
