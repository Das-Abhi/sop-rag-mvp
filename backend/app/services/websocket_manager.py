# WebSocket manager
"""
WebSocket connection management for real-time updates
"""
from typing import Dict, Any, List
from fastapi import WebSocket
from loguru import logger
import json
import asyncio


class WebSocketManager:
    """Manages WebSocket connections for real-time updates"""

    def __init__(self):
        """Initialize WebSocket manager"""
        self.active_connections: Dict[str, WebSocket] = {}
        self.client_subscriptions: Dict[str, set] = {}  # client_id -> set of document_ids

    async def connect(self, client_id: str, websocket: WebSocket) -> None:
        """Register new WebSocket connection"""
        try:
            await websocket.accept()
            self.active_connections[client_id] = websocket
            self.client_subscriptions[client_id] = set()
            logger.info(f"WebSocket connected: {client_id}")
        except Exception as e:
            logger.error(f"Error accepting WebSocket connection: {e}")
            raise

    def disconnect(self, client_id: str) -> None:
        """Unregister WebSocket connection"""
        try:
            if client_id in self.active_connections:
                del self.active_connections[client_id]
            if client_id in self.client_subscriptions:
                del self.client_subscriptions[client_id]
            logger.info(f"WebSocket disconnected: {client_id}")
        except Exception as e:
            logger.error(f"Error disconnecting WebSocket: {e}")

    def subscribe(self, client_id: str, document_id: str) -> None:
        """Subscribe client to document updates"""
        if client_id not in self.client_subscriptions:
            self.client_subscriptions[client_id] = set()
        self.client_subscriptions[client_id].add(document_id)
        logger.debug(f"Client {client_id} subscribed to {document_id}")

    def unsubscribe(self, client_id: str, document_id: str) -> None:
        """Unsubscribe client from document updates"""
        if client_id in self.client_subscriptions:
            self.client_subscriptions[client_id].discard(document_id)
            logger.debug(f"Client {client_id} unsubscribed from {document_id}")

    async def broadcast(self, message: Dict) -> None:
        """Broadcast message to all connected clients"""
        disconnected = []
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Error broadcasting to {client_id}: {e}")
                disconnected.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id)

    async def send_to_client(self, client_id: str, message: Dict) -> None:
        """Send message to specific client"""
        if client_id not in self.active_connections:
            logger.warning(f"Client {client_id} not connected")
            return

        try:
            await self.active_connections[client_id].send_json(message)
            logger.debug(f"Message sent to {client_id}")
        except Exception as e:
            logger.error(f"Error sending to {client_id}: {e}")
            self.disconnect(client_id)

    async def send_processing_update(
        self,
        document_id: str,
        progress: int,
        status: str,
        current_step: str = None,
        details: Dict = None
    ) -> None:
        """Send processing progress update to subscribed clients"""
        message = {
            "type": "processing_update",
            "document_id": document_id,
            "progress": progress,
            "status": status,
            "current_step": current_step,
            "details": details or {}
        }

        # Send to all clients subscribed to this document
        disconnected = []
        for client_id, subscriptions in self.client_subscriptions.items():
            if document_id in subscriptions:
                try:
                    await self.send_to_client(client_id, message)
                except Exception as e:
                    logger.warning(f"Error sending update to {client_id}: {e}")
                    disconnected.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id)

    async def send_error(self, client_id: str, error_message: str, document_id: str = None) -> None:
        """Send error message to client"""
        message = {
            "type": "error",
            "message": error_message,
            "document_id": document_id
        }
        await self.send_to_client(client_id, message)
        logger.warning(f"Error sent to {client_id}: {error_message}")

    async def send_query_response(
        self,
        client_id: str,
        response: str,
        citations: List[Dict],
        metadata: Dict = None
    ) -> None:
        """Send query response to client"""
        message = {
            "type": "query_response",
            "response": response,
            "citations": citations,
            "metadata": metadata or {}
        }
        await self.send_to_client(client_id, message)

    async def send_chat_chunk(self, client_id: str, chunk: str, message_id: str = None) -> None:
        """Send streaming chat response chunk"""
        message = {
            "type": "chat_chunk",
            "chunk": chunk,
            "message_id": message_id
        }
        await self.send_to_client(client_id, message)

    def get_active_connections_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)

    def get_connection_info(self) -> Dict:
        """Get information about active connections"""
        return {
            "total_connections": len(self.active_connections),
            "clients": list(self.active_connections.keys()),
            "subscriptions": {
                client_id: list(subs)
                for client_id, subs in self.client_subscriptions.items()
            }
        }


# Global WebSocket manager instance
ws_manager = WebSocketManager()
