"""
ADB Device Manager
Manages device discovery, connection pooling, and lifecycle
"""

import asyncio
from typing import Dict, List, Optional

from scws.config import settings
from scws.models import ADBDevice
from scws.utils import ADBConnectionError, ADBDeviceNotFoundError, get_logger

from .connection import ADBConnection

logger = get_logger(__name__)


class ADBDeviceManager:
    """Manages ADB device connections"""

    def __init__(self) -> None:
        self._connections: Dict[str, ADBConnection] = {}
        self._devices: Dict[str, ADBDevice] = {}
        self._polling_task: Optional[asyncio.Task[None]] = None
        self._running = False

    async def initialize(self) -> None:
        """Initialize the device manager"""
        try:
            logger.info("Initializing ADB device manager")

            # Start device polling
            await self.poll_devices()
            self._start_polling()

            logger.info("ADB device manager initialized")
        except Exception as e:
            logger.error("Failed to initialize device manager", error=str(e))
            raise ADBConnectionError("Failed to initialize device manager", details=str(e))

    async def shutdown(self) -> None:
        """Shutdown the device manager"""
        logger.info("Shutting down device manager")

        self._running = False

        # Cancel polling task
        if self._polling_task:
            self._polling_task.cancel()
            try:
                await self._polling_task
            except asyncio.CancelledError:
                pass

        # Disconnect all devices
        disconnect_tasks = [conn.disconnect() for conn in self._connections.values()]
        await asyncio.gather(*disconnect_tasks, return_exceptions=True)

        self._connections.clear()
        self._devices.clear()

        logger.info("Device manager shut down")

    async def list_devices(self) -> List[ADBDevice]:
        """List all connected devices"""
        return list(self._devices.values())

    def get_device(self, serial: str) -> Optional[ADBDevice]:
        """Get device by serial"""
        return self._devices.get(serial)

    def get_connection(self, serial: str) -> ADBConnection:
        """Get connection by serial"""
        connection = self._connections.get(serial)
        if not connection:
            raise ADBDeviceNotFoundError(serial)
        return connection

    async def connect_to_device(self, serial: str) -> ADBConnection:
        """Connect to a device"""
        logger.info("Connecting to device", serial=serial)

        # Check if already connected
        existing_connection = self._connections.get(serial)
        if existing_connection and existing_connection.is_connected:
            logger.info("Device already connected", serial=serial)
            return existing_connection

        # Create new connection
        connection = ADBConnection(serial, host=settings.adb_host, port=settings.adb_port)
        await connection.connect()

        # Get device info
        device_info = await connection.get_device_info()

        # Store connection and device info
        self._connections[serial] = connection
        self._devices[serial] = device_info

        logger.info("Device connected", serial=serial, model=device_info.model)

        return connection

    async def disconnect_from_device(self, serial: str) -> None:
        """Disconnect from a device"""
        logger.info("Disconnecting from device", serial=serial)

        connection = self._connections.get(serial)
        if connection:
            await connection.disconnect()
            del self._connections[serial]

        if serial in self._devices:
            del self._devices[serial]

        logger.info("Device disconnected", serial=serial)

    async def poll_devices(self) -> None:
        """Poll for device changes"""
        try:
            # In a real implementation, you would use ADB to list devices
            # For now, we'll manage connected devices manually
            # This is a simplified version - in production, you'd call
            # `adb devices` via subprocess or use adb-shell's device listing

            # Health check for existing connections
            health_tasks = {
                serial: conn.health_check() for serial, conn in self._connections.items()
            }

            results = await asyncio.gather(*health_tasks.values(), return_exceptions=True)

            for serial, is_healthy in zip(health_tasks.keys(), results):
                if isinstance(is_healthy, bool) and not is_healthy:
                    logger.warning("Device unhealthy, disconnecting", serial=serial)
                    await self.disconnect_from_device(serial)

        except Exception as e:
            logger.error("Error polling devices", error=str(e))

    def _start_polling(self) -> None:
        """Start device polling task"""
        if self._polling_task:
            return

        self._running = True

        async def poll_loop() -> None:
            while self._running:
                try:
                    await self.poll_devices()
                    await asyncio.sleep(2)  # Poll every 2 seconds
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error("Error in polling loop", error=str(e))
                    await asyncio.sleep(5)  # Back off on error

        self._polling_task = asyncio.create_task(poll_loop())
        logger.debug("Device polling started")


# Singleton instance
device_manager = ADBDeviceManager()
