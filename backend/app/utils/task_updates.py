"""
Utility functions for task progress updates via WebSocket
"""
import asyncio
from loguru import logger
from app.services.websocket_manager import ws_manager


def get_event_loop():
    """Get or create event loop for async operations"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop


async def notify_processing_update(
    document_id: str,
    progress: int,
    status: str,
    current_step: str = None,
    details: dict = None
):
    """
    Send processing update to all subscribed WebSocket clients

    Args:
        document_id: Document being processed
        progress: Progress percentage (0-100)
        status: Current status (pending/processing/completed/error)
        current_step: Current processing step
        details: Additional details
    """
    try:
        await ws_manager.send_processing_update(
            document_id=document_id,
            progress=progress,
            status=status,
            current_step=current_step,
            details=details
        )
        logger.debug(f"Update sent for {document_id}: {progress}% - {current_step}")
    except Exception as e:
        logger.warning(f"Error sending update: {e}")


def send_processing_update_sync(
    document_id: str,
    progress: int,
    status: str,
    current_step: str = None,
    details: dict = None
):
    """
    Synchronous wrapper for sending processing updates from Celery tasks

    Args:
        document_id: Document being processed
        progress: Progress percentage (0-100)
        status: Current status
        current_step: Current processing step
        details: Additional details
    """
    try:
        loop = get_event_loop()
        # Check if loop is running
        if loop.is_running():
            # Schedule coroutine to run in the loop
            asyncio.run_coroutine_threadsafe(
                notify_processing_update(
                    document_id=document_id,
                    progress=progress,
                    status=status,
                    current_step=current_step,
                    details=details
                ),
                loop
            )
        else:
            # Run coroutine directly
            loop.run_until_complete(
                notify_processing_update(
                    document_id=document_id,
                    progress=progress,
                    status=status,
                    current_step=current_step,
                    details=details
                )
            )
    except Exception as e:
        logger.warning(f"Could not send processing update: {e}")


async def notify_error(client_id: str, error_message: str, document_id: str = None):
    """
    Send error notification to client

    Args:
        client_id: Client to notify
        error_message: Error message
        document_id: Associated document ID
    """
    try:
        await ws_manager.send_error(client_id, error_message, document_id)
        logger.debug(f"Error notification sent to {client_id}")
    except Exception as e:
        logger.warning(f"Error sending error notification: {e}")


async def notify_query_response(
    client_id: str,
    response: str,
    citations: list,
    metadata: dict = None
):
    """
    Send query response to client

    Args:
        client_id: Client to notify
        response: Response text
        citations: List of citations
        metadata: Additional metadata
    """
    try:
        await ws_manager.send_query_response(
            client_id=client_id,
            response=response,
            citations=citations,
            metadata=metadata
        )
        logger.debug(f"Query response sent to {client_id}")
    except Exception as e:
        logger.warning(f"Error sending query response: {e}")


async def stream_chat_response(
    client_id: str,
    response_generator,
    message_id: str = None
):
    """
    Stream chat response in chunks

    Args:
        client_id: Client to stream to
        response_generator: Generator or iterable of response chunks
        message_id: Message identifier
    """
    try:
        for chunk in response_generator:
            await ws_manager.send_chat_chunk(
                client_id=client_id,
                chunk=chunk,
                message_id=message_id
            )
            # Small delay to avoid overwhelming client
            await asyncio.sleep(0.01)

        # Send completion message
        await ws_manager.send_chat_chunk(
            client_id=client_id,
            chunk="[COMPLETE]",
            message_id=message_id
        )
        logger.debug(f"Chat stream completed for {client_id}")
    except Exception as e:
        logger.error(f"Error streaming chat response: {e}")
