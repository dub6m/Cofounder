"""
WebSocket connection manager and event router.
Handles connection lifecycle, event dispatch, and broadcasting.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import WebSocket, WebSocketDisconnect

from schemas.ws_events import EventType, WsEnvelope

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages active WebSocket connections.
    Single-user MVP: maintains one active connection.
    Multi-tenant ready: keyed by session/user ID for future scaling.
    """

    def __init__(self):
        self._activeConnections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, clientId: str = "default"):
        await websocket.accept()
        self._activeConnections[clientId] = websocket
        logger.info(f"WebSocket connected: {clientId}")

    def disconnect(self, clientId: str = "default"):
        self._activeConnections.pop(clientId, None)
        logger.info(f"WebSocket disconnected: {clientId}")

    async def sendEvent(
        self,
        eventType: EventType,
        payload: dict,
        clientId: str = "default",
    ):
        """Send a typed event to a specific client."""
        envelope = WsEnvelope(
            event_type=eventType,
            timestamp=datetime.now(timezone.utc).isoformat(),
            payload=payload,
        )
        ws = self._activeConnections.get(clientId)
        if ws:
            try:
                await ws.send_text(envelope.model_dump_json(by_alias=True))
            except Exception as e:
                logger.error(f"Failed to send to {clientId}: {e}")
                self.disconnect(clientId)

    async def broadcast(self, eventType: EventType, payload: dict):
        """Send an event to ALL connected clients."""
        disconnected = []
        for clientId, ws in self._activeConnections.items():
            try:
                envelope = WsEnvelope(
                    event_type=eventType,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    payload=payload,
                )
                await ws.send_text(envelope.model_dump_json(by_alias=True))
            except Exception:
                disconnected.append(clientId)
        for cid in disconnected:
            self.disconnect(cid)

    def isConnected(self, clientId: str = "default") -> bool:
        return clientId in self._activeConnections


# Global singleton
manager = ConnectionManager()
