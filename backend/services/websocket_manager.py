"""
WebSocket Manager Service
Real-time updates and live dashboard updates
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.connection_metadata: Dict[WebSocket, Dict] = {}
    
    async def connect(self, websocket: WebSocket, room: str = "default", user_id: str = None):
        """Accept WebSocket connection"""
        await websocket.accept()
        
        if room not in self.active_connections:
            self.active_connections[room] = set()
        
        self.active_connections[room].add(websocket)
        self.connection_metadata[websocket] = {
            "room": room,
            "user_id": user_id,
            "connected_at": datetime.now().isoformat()
        }
        
        logger.info(f"WebSocket connected: room={room}, user_id={user_id}")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection",
            "status": "connected",
            "room": room,
            "timestamp": datetime.now().isoformat()
        }, websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.connection_metadata:
            metadata = self.connection_metadata[websocket]
            room = metadata["room"]
            
            if room in self.active_connections:
                self.active_connections[room].discard(websocket)
                if not self.active_connections[room]:
                    del self.active_connections[room]
            
            del self.connection_metadata[websocket]
            logger.info(f"WebSocket disconnected: room={room}")
    
    async def send_personal_message(self, message: Dict, websocket: WebSocket):
        """Send message to specific WebSocket"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: Dict, room: str = "default"):
        """Broadcast message to all connections in a room"""
        if room not in self.active_connections:
            return
        
        disconnected = set()
        for connection in self.active_connections[room]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.add(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            self.disconnect(conn)
    
    async def broadcast_to_all(self, message: Dict):
        """Broadcast message to all connections"""
        for room in list(self.active_connections.keys()):
            await self.broadcast(message, room)
    
    def get_connection_count(self, room: str = None) -> int:
        """Get number of active connections"""
        if room:
            return len(self.active_connections.get(room, set()))
        return sum(len(conns) for conns in self.active_connections.values())
    
    def get_rooms(self) -> List[str]:
        """Get list of active rooms"""
        return list(self.active_connections.keys())


# Singleton instance
websocket_manager = WebSocketManager()


class RealTimeUpdateService:
    """Service for sending real-time updates via WebSocket"""
    
    def __init__(self):
        self.manager = websocket_manager
    
    async def send_supplier_update(self, supplier_id: str, data: Dict):
        """Send supplier update to dashboard room"""
        message = {
            "type": "supplier_update",
            "supplier_id": supplier_id,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        await self.manager.broadcast(message, room="dashboard")
    
    async def send_risk_alert(self, alert_data: Dict):
        """Send risk alert"""
        message = {
            "type": "risk_alert",
            "alert": alert_data,
            "timestamp": datetime.now().isoformat()
        }
        await self.manager.broadcast(message, room="dashboard")
    
    async def send_fraud_alert(self, alert_data: Dict):
        """Send fraud alert"""
        message = {
            "type": "fraud_alert",
            "alert": alert_data,
            "timestamp": datetime.now().isoformat()
        }
        await self.manager.broadcast(message, room="dashboard")
    
    async def send_model_update(self, model_type: str, update_data: Dict):
        """Send model training/prediction update"""
        message = {
            "type": "model_update",
            "model_type": model_type,
            "data": update_data,
            "timestamp": datetime.now().isoformat()
        }
        await self.manager.broadcast(message, room="dashboard")
    
    async def send_dashboard_update(self, dashboard_data: Dict):
        """Send general dashboard update"""
        message = {
            "type": "dashboard_update",
            "data": dashboard_data,
            "timestamp": datetime.now().isoformat()
        }
        await self.manager.broadcast(message, room="dashboard")


# Singleton instance
realtime_update_service = RealTimeUpdateService()

