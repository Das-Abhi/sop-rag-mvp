"""
WebSocket endpoint for real-time communication
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from loguru import logger
import uuid
import json

from app.services.websocket_manager import ws_manager
from app.crud import ProcessingTaskCRUD, DocumentCRUD
from app.database import SessionLocal

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates

    Client can:
    1. Subscribe to document updates: {"action": "subscribe", "document_id": "..."}
    2. Unsubscribe: {"action": "unsubscribe", "document_id": "..."}
    3. Get status: {"action": "status", "document_id": "..."}
    """
    # Generate unique client ID
    client_id = str(uuid.uuid4())

    # Connect client
    await ws_manager.connect(client_id, websocket)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                action = message.get("action")
                document_id = message.get("document_id")

                logger.debug(f"WebSocket message from {client_id}: {action}")

                if action == "subscribe":
                    if not document_id:
                        await ws_manager.send_error(client_id, "document_id required for subscribe")
                        continue

                    ws_manager.subscribe(client_id, document_id)

                    # Send confirmation
                    await websocket.send_json({
                        "type": "subscription_confirmed",
                        "document_id": document_id,
                        "client_id": client_id
                    })

                    # Send current status
                    db = SessionLocal()
                    try:
                        doc = DocumentCRUD.get(db, document_id)
                        if doc:
                            await websocket.send_json({
                                "type": "document_status",
                                "document_id": document_id,
                                "status": doc.status,
                                "chunks": doc.total_chunks,
                                "created_at": doc.created_at.isoformat()
                            })
                    finally:
                        db.close()

                elif action == "unsubscribe":
                    if not document_id:
                        await ws_manager.send_error(client_id, "document_id required for unsubscribe")
                        continue

                    ws_manager.unsubscribe(client_id, document_id)

                    await websocket.send_json({
                        "type": "unsubscription_confirmed",
                        "document_id": document_id
                    })

                elif action == "status":
                    if not document_id:
                        await ws_manager.send_error(client_id, "document_id required for status")
                        continue

                    db = SessionLocal()
                    try:
                        doc = DocumentCRUD.get(db, document_id)
                        if doc:
                            await websocket.send_json({
                                "type": "document_status",
                                "document_id": document_id,
                                "status": doc.status,
                                "chunks": doc.total_chunks,
                                "created_at": doc.created_at.isoformat(),
                                "error_message": doc.error_message
                            })
                        else:
                            await ws_manager.send_error(client_id, f"Document {document_id} not found")
                    finally:
                        db.close()

                elif action == "ping":
                    # Heartbeat/keep-alive
                    await websocket.send_json({"type": "pong"})

                else:
                    await ws_manager.send_error(client_id, f"Unknown action: {action}")

            except json.JSONDecodeError:
                await ws_manager.send_error(client_id, "Invalid JSON format")
            except Exception as e:
                logger.error(f"Error processing message from {client_id}: {e}")
                await ws_manager.send_error(client_id, f"Error: {str(e)}")

    except WebSocketDisconnect:
        ws_manager.disconnect(client_id)
        logger.info(f"Client disconnected: {client_id}")

    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        ws_manager.disconnect(client_id)


@router.get("/ws/info")
async def websocket_info():
    """
    Get WebSocket connection information

    Returns:
        Connection statistics and active clients
    """
    return ws_manager.get_connection_info()


@router.post("/ws/broadcast")
async def broadcast_message(message: dict):
    """
    Broadcast message to all connected clients (admin endpoint)

    Args:
        message: Message to broadcast

    Returns:
        Broadcast confirmation
    """
    await ws_manager.broadcast(message)
    return {"status": "broadcast_sent", "recipients": ws_manager.get_active_connections_count()}
