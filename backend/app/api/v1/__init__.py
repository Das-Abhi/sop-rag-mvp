"""
API v1 routes
"""
from . import documents
from . import query
from . import processing
from . import websocket

__all__ = ["documents", "query", "processing", "websocket"]
