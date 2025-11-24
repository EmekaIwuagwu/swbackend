"""
WebSocket message models
"""

from enum import Enum
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field


class WSMessageType(str, Enum):
    """WebSocket message types"""

    VIDEO_FRAME = "video_frame"
    AUDIO_FRAME = "audio_frame"
    CONTROL_EVENT = "control_event"
    DEVICE_INFO = "device_info"
    STREAM_STATUS = "stream_status"
    ERROR = "error"
    PING = "ping"
    PONG = "pong"


T = TypeVar("T")


class WSMessage(BaseModel, Generic[T]):
    """Base WebSocket message"""

    type: WSMessageType = Field(..., description="Message type")
    timestamp: int = Field(..., description="Timestamp in milliseconds")
    data: T = Field(..., description="Message payload")


class VideoFrameData(BaseModel):
    """Video frame data"""

    sequence: int = Field(..., description="Frame sequence number")
    pts: int = Field(..., description="Presentation timestamp")
    is_keyframe: bool = Field(..., description="Is this a keyframe")
    # Frame data is sent as binary, not in JSON


class AudioFrameData(BaseModel):
    """Audio frame data"""

    sequence: int = Field(..., description="Frame sequence number")
    pts: int = Field(..., description="Presentation timestamp")
    # Audio data is sent as binary, not in JSON


class Resolution(BaseModel):
    """Screen resolution"""

    width: int
    height: int


class DeviceInfoData(BaseModel):
    """Device information"""

    serial: str = Field(..., description="Device serial")
    model: str = Field(..., description="Device model")
    manufacturer: Optional[str] = Field(None, description="Device manufacturer")
    android_version: Optional[str] = Field(None, description="Android version")
    resolution: Resolution = Field(..., description="Screen resolution")
    video_codec: str = Field(..., description="Video codec")
    audio_codec: str = Field(..., description="Audio codec")


class StreamStatusData(BaseModel):
    """Stream status information"""

    serial: str = Field(..., description="Device serial")
    active: bool = Field(..., description="Is streaming active")
    client_count: int = Field(..., description="Number of connected clients")
    fps: Optional[float] = Field(None, description="Current frame rate")
    video_bitrate: Optional[int] = Field(None, description="Video bitrate")
    audio_bitrate: Optional[int] = Field(None, description="Audio bitrate")


class ErrorMessageData(BaseModel):
    """Error message data"""

    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Any] = Field(None, description="Additional error details")


class ControlEventType(str, Enum):
    """Control event types"""

    TOUCH_DOWN = "touch_down"
    TOUCH_UP = "touch_up"
    TOUCH_MOVE = "touch_move"
    SCROLL = "scroll"
    KEY_DOWN = "key_down"
    KEY_UP = "key_up"
    TEXT_INPUT = "text_input"
    BACK = "back"
    HOME = "home"
    APP_SWITCH = "app_switch"
    POWER = "power"
    VOLUME_UP = "volume_up"
    VOLUME_DOWN = "volume_down"
    ROTATE = "rotate"


class TouchPosition(BaseModel):
    """Touch position coordinates"""

    x: float = Field(..., ge=0.0, le=1.0, description="X coordinate (normalized 0-1)")
    y: float = Field(..., ge=0.0, le=1.0, description="Y coordinate (normalized 0-1)")


class ControlEvent(BaseModel):
    """Control event base"""

    type: ControlEventType = Field(..., description="Event type")
    timestamp: int = Field(..., description="Event timestamp")
    position: Optional[TouchPosition] = Field(None, description="Touch position")
    pointer_id: Optional[int] = Field(None, description="Pointer ID for multi-touch")
    pressure: Optional[float] = Field(None, description="Touch pressure (0-1)")
    delta_x: Optional[float] = Field(None, description="Horizontal scroll delta")
    delta_y: Optional[float] = Field(None, description="Vertical scroll delta")
    key_code: Optional[int] = Field(None, description="Android key code")
    meta_state: Optional[int] = Field(None, description="Meta state (shift, ctrl, etc.)")
    text: Optional[str] = Field(None, description="Text input")
    rotation: Optional[int] = Field(None, description="Target rotation (0-3)")
