"""
WebSocket router and handlers
"""

import asyncio
from datetime import datetime
from typing import Dict, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

from scws.models import (
    ControlEvent,
    DeviceInfoData,
    ErrorMessageData,
    Resolution,
    WSMessage,
    WSMessageType,
)
from scws.utils import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Track active WebSocket connections per device
active_connections: Dict[str, Set[WebSocket]] = {}


class ConnectionManager:
    """Manage WebSocket connections"""

    def __init__(self) -> None:
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, serial: str) -> None:
        """Connect a new WebSocket client"""
        await websocket.accept()

        if serial not in self.active_connections:
            self.active_connections[serial] = set()

        self.active_connections[serial].add(websocket)

        logger.info(
            "WebSocket client connected",
            serial=serial,
            client_count=len(self.active_connections[serial]),
        )

    async def disconnect(self, websocket: WebSocket, serial: str) -> None:
        """Disconnect a WebSocket client"""
        if serial in self.active_connections:
            self.active_connections[serial].discard(websocket)

            if not self.active_connections[serial]:
                del self.active_connections[serial]

            logger.info(
                "WebSocket client disconnected",
                serial=serial,
                remaining_clients=len(self.active_connections.get(serial, [])),
            )

    async def send_message(self, message: WSMessage[object], serial: str) -> None:
        """Send message to all clients for a device"""
        if serial not in self.active_connections:
            return

        disconnected: Set[WebSocket] = set()

        for websocket in self.active_connections[serial]:
            try:
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_json(message.model_dump())
                else:
                    disconnected.add(websocket)
            except Exception as e:
                logger.error("Error sending message to client", error=str(e))
                disconnected.add(websocket)

        # Remove disconnected clients
        for websocket in disconnected:
            await self.disconnect(websocket, serial)

    async def send_binary(self, data: bytes, serial: str) -> None:
        """Send binary data to all clients for a device"""
        if serial not in self.active_connections:
            return

        disconnected: Set[WebSocket] = set()

        for websocket in self.active_connections[serial]:
            try:
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_bytes(data)
                else:
                    disconnected.add(websocket)
            except Exception as e:
                logger.error("Error sending binary to client", error=str(e))
                disconnected.add(websocket)

        # Remove disconnected clients
        for websocket in disconnected:
            await self.disconnect(websocket, serial)


manager = ConnectionManager()


@router.websocket("/stream/{serial}")
async def websocket_stream(websocket: WebSocket, serial: str) -> None:
    """WebSocket endpoint for video/audio streaming"""
    await manager.connect(websocket, serial)

    try:
        # Send device info
        device_info = DeviceInfoData(
            serial=serial,
            model="Test Device",  # TODO: Get from device manager
            resolution=Resolution(width=1080, height=1920),
            video_codec="h264",
            audio_codec="opus",
        )

        device_info_msg: WSMessage[DeviceInfoData] = WSMessage(
            type=WSMessageType.DEVICE_INFO,
            timestamp=int(datetime.now().timestamp() * 1000),
            data=device_info,
        )

        await websocket.send_json(device_info_msg.model_dump())

        # Handle incoming messages
        while True:
            try:
                # Receive message from client
                message = await websocket.receive_text()

                # Parse message (would contain control events in production)
                logger.debug("Received message from client", serial=serial, message=message)

                # Echo back for testing
                await websocket.send_text(message)

            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error("Error in WebSocket loop", error=str(e))
                error_msg: WSMessage[ErrorMessageData] = WSMessage(
                    type=WSMessageType.ERROR,
                    timestamp=int(datetime.now().timestamp() * 1000),
                    data=ErrorMessageData(
                        code="WEBSOCKET_ERROR",
                        message=str(e),
                    ),
                )
                await websocket.send_json(error_msg.model_dump())
                break

    finally:
        await manager.disconnect(websocket, serial)


@router.websocket("/control/{serial}")
async def websocket_control(websocket: WebSocket, serial: str) -> None:
    """WebSocket endpoint for control events"""
    await manager.connect(websocket, serial)

    try:
        while True:
            try:
                # Receive control event from client
                data = await websocket.receive_json()

                # Parse control event
                control_event = ControlEvent(**data)

                logger.debug(
                    "Received control event",
                    serial=serial,
                    event_type=control_event.type.value,
                )

                # TODO: Process control event and send to device

                # Acknowledge
                await websocket.send_json({"status": "ok"})

            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error("Error processing control event", error=str(e))
                await websocket.send_json({"status": "error", "message": str(e)})

    finally:
        await manager.disconnect(websocket, serial)
