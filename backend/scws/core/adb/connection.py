"""
ADB Connection wrapper using adb-shell
"""

import asyncio
from datetime import datetime
from typing import Optional

from adb_shell.adb_device_async import AdbDeviceTcpAsync
from adb_shell.auth.sign_pythonrsa import PythonRSASigner

from scws.models import ADBDevice, DeviceState, Resolution
from scws.utils import ADBDeviceOfflineError, get_logger

logger = get_logger(__name__)


class ADBConnection:
    """ADB connection wrapper for a single device"""

    def __init__(self, serial: str, host: str = "127.0.0.1", port: int = 5037) -> None:
        self.serial = serial
        self.host = host
        self.port = self._parse_port_from_serial(serial, port)
        self._device: Optional[AdbDeviceTcpAsync] = None
        self._connected = False
        self._connection_time: Optional[datetime] = None
        self._last_activity: Optional[datetime] = None

    @staticmethod
    def _parse_port_from_serial(serial: str, default_port: int) -> int:
        """Parse port from serial if it contains host:port format"""
        if ":" in serial:
            try:
                return int(serial.split(":")[1])
            except (IndexError, ValueError):
                pass
        return default_port

    @property
    def is_connected(self) -> bool:
        """Check if device is connected"""
        return self._connected and self._device is not None

    @property
    def connection_time(self) -> Optional[datetime]:
        """Get connection timestamp"""
        return self._connection_time

    @property
    def last_activity(self) -> Optional[datetime]:
        """Get last activity timestamp"""
        return self._last_activity

    async def connect(self) -> None:
        """Connect to the device"""
        try:
            logger.info("Connecting to device", serial=self.serial)

            # Create ADB device instance
            self._device = AdbDeviceTcpAsync(host=self.host, port=self.port, default_timeout_s=10)

            # Try to connect with RSA keys if available
            rsa_keys = []
            try:
                import os
                key_path = os.path.expanduser("~/.android/adbkey")
                if os.path.exists(key_path):
                    signer = PythonRSASigner.FromRSAKeyPath(key_path)
                    rsa_keys = [signer]
            except Exception:
                pass  # Continue without keys

            await self._device.connect(rsa_keys=rsa_keys, auth_timeout_s=10)

            self._connected = True
            self._connection_time = datetime.now()
            self._last_activity = datetime.now()

            logger.info("Device connected successfully", serial=self.serial)
        except Exception as e:
            logger.error("Failed to connect to device", serial=self.serial, error=str(e))
            self._connected = False
            raise

    async def disconnect(self) -> None:
        """Disconnect from the device"""
        try:
            logger.info("Disconnecting from device", serial=self.serial)

            if self._device:
                await self._device.close()
                self._device = None

            self._connected = False

            logger.info("Device disconnected", serial=self.serial)
        except Exception as e:
            logger.error("Error during disconnect", serial=self.serial, error=str(e))
            raise

    async def shell(self, command: str) -> str:
        """Execute shell command on device"""
        if not self.is_connected or not self._device:
            raise ADBDeviceOfflineError(self.serial)

        self._last_activity = datetime.now()

        try:
            result = await self._device.shell(command)
            return result
        except Exception as e:
            logger.error(
                "Shell command failed", serial=self.serial, command=command, error=str(e)
            )
            raise

    async def push(self, local_path: str, device_path: str) -> None:
        """Push file to device"""
        if not self.is_connected or not self._device:
            raise ADBDeviceOfflineError(self.serial)

        self._last_activity = datetime.now()

        try:
            with open(local_path, "rb") as f:
                data = f.read()
                await self._device.push(data, device_path)
        except Exception as e:
            logger.error("Push failed", serial=self.serial, error=str(e))
            raise

    async def pull(self, device_path: str, local_path: str) -> None:
        """Pull file from device"""
        if not self.is_connected or not self._device:
            raise ADBDeviceOfflineError(self.serial)

        self._last_activity = datetime.now()

        try:
            data = await self._device.pull(device_path)
            with open(local_path, "wb") as f:
                f.write(data)
        except Exception as e:
            logger.error("Pull failed", serial=self.serial, error=str(e))
            raise

    async def get_device_info(self) -> ADBDevice:
        """Get device information"""
        model = (await self.shell("getprop ro.product.model")).strip()
        manufacturer = (await self.shell("getprop ro.product.manufacturer")).strip()
        android_version = (await self.shell("getprop ro.build.version.release")).strip()

        # Get screen resolution
        wm_size = await self.shell("wm size")
        resolution: Optional[Resolution] = None
        if "Physical size:" in wm_size:
            try:
                size_str = wm_size.split("Physical size:")[1].strip()
                width, height = size_str.split("x")
                resolution = Resolution(width=int(width), height=int(height))
            except (IndexError, ValueError):
                pass

        return ADBDevice(
            id=self.serial,
            serial=self.serial,
            model=model,
            state=DeviceState.DEVICE,
            transport_type="wifi" if ":" in self.serial else "usb",
            connection_time=self._connection_time or datetime.now(),
            manufacturer=manufacturer,
            android_version=android_version,
            resolution=resolution,
        )

    async def health_check(self) -> bool:
        """Check device health"""
        try:
            if not self.is_connected:
                return False

            await self.shell("echo ping")
            self._last_activity = datetime.now()
            return True
        except Exception:
            return False
