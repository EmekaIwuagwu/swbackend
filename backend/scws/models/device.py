"""
Device-related Pydantic models
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DeviceState(str, Enum):
    """Device connection state"""

    DEVICE = "device"
    OFFLINE = "offline"
    UNAUTHORIZED = "unauthorized"


class TransportType(str, Enum):
    """Connection transport type"""

    USB = "usb"
    WIFI = "wifi"


class Resolution(BaseModel):
    """Screen resolution"""

    width: int = Field(..., description="Screen width in pixels")
    height: int = Field(..., description="Screen height in pixels")


class ADBDevice(BaseModel):
    """Android device connected via ADB"""

    id: str = Field(..., description="Unique device identifier")
    serial: str = Field(..., description="Device serial number")
    model: str = Field(..., description="Device model name")
    state: DeviceState = Field(..., description="Current connection state")
    transport_type: TransportType = Field(..., description="Connection transport type")
    connection_time: datetime = Field(..., description="Connection timestamp")
    manufacturer: Optional[str] = Field(None, description="Device manufacturer")
    android_version: Optional[str] = Field(None, description="Android version")
    resolution: Optional[Resolution] = Field(None, description="Screen resolution")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "emulator-5554",
                "serial": "emulator-5554",
                "model": "Android SDK built for x86",
                "state": "device",
                "transport_type": "usb",
                "connection_time": "2024-01-01T12:00:00Z",
                "manufacturer": "Google",
                "android_version": "13",
                "resolution": {"width": 1080, "height": 1920},
            }
        }


class DeviceConnectionOptions(BaseModel):
    """Options for device connection"""

    serial: str = Field(..., description="Device serial number")
    timeout: int = Field(default=30000, description="Connection timeout in milliseconds")
    auto_reconnect: bool = Field(default=True, description="Enable auto-reconnect")
