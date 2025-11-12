"""
API Routes for WebSocket
Real-time updates and live dashboard
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Optional
from services.websocket_manager import websocket_manager, realtime_update_service
import json

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, room: str = "default", user_id: Optional[str] = None):
    """
    WebSocket endpoint for real-time updates
    
    Args:
        websocket: WebSocket connection
        room: Room/channel name (default: "default")
        user_id: Optional user ID
    """
    await websocket_manager.connect(websocket, room=room, user_id=user_id)
    
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                message_type = message.get("type")
                
                # Handle different message types
                if message_type == "ping":
                    await websocket_manager.send_personal_message({
                        "type": "pong",
                        "timestamp": message.get("timestamp")
                    }, websocket)
                
                elif message_type == "subscribe":
                    # Subscribe to specific updates
                    subscribe_to = message.get("subscribe", [])
                    await websocket_manager.send_personal_message({
                        "type": "subscribed",
                        "channels": subscribe_to
                    }, websocket)
                
                elif message_type == "unsubscribe":
                    # Unsubscribe from updates
                    unsubscribe_from = message.get("unsubscribe", [])
                    await websocket_manager.send_personal_message({
                        "type": "unsubscribed",
                        "channels": unsubscribe_from
                    }, websocket)
                
            except json.JSONDecodeError:
                await websocket_manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format"
                }, websocket)
                
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        websocket_manager.disconnect(websocket)
        raise


@router.websocket("/ws/dashboard")
async def dashboard_websocket(websocket: WebSocket, user_id: Optional[str] = None):
    """
    WebSocket endpoint specifically for dashboard updates
    
    Args:
        websocket: WebSocket connection
        user_id: Optional user ID
    """
    await websocket_endpoint(websocket, room="dashboard", user_id=user_id)


@router.websocket("/ws/alerts")
async def alerts_websocket(websocket: WebSocket, user_id: Optional[str] = None):
    """
    WebSocket endpoint for real-time alerts
    
    Args:
        websocket: WebSocket connection
        user_id: Optional user ID
    """
    await websocket_endpoint(websocket, room="alerts", user_id=user_id)


@router.get("/ws/stats")
async def get_websocket_stats():
    """
    Get WebSocket connection statistics
    
    Returns:
        Statistics about active connections
    """
    try:
        rooms = websocket_manager.get_rooms()
        stats = {}
        
        for room in rooms:
            stats[room] = websocket_manager.get_connection_count(room)
        
        return {
            "success": True,
            "total_connections": websocket_manager.get_connection_count(),
            "rooms": stats,
            "active_rooms": rooms
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

