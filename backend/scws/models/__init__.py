"""
Pydantic models for request/response schemas
"""


from .device import (
    ADBDevice,
    DeviceConnectionOptions,
    DeviceState,
    Resolution,
    TransportType,
)
from .scrcpy import (
    AudioCodec,
    ScrcpyConfig,
    ScrcpyServerState,
    ScrcpyServerStatus,
    VideoCodec,
)
from .websocket import (
    AudioFrameData,
    ControlEvent,
    ControlEventType,
    DeviceInfoData,
    ErrorMessageData,
    StreamStatusData,
    VideoFrameData,
    WSMessage,
    WSMessageType,
)
from .api import (
    DeviceStats,
    ErrorResponse,
    HealthCheckResponse,
    MemoryUsage,
    MetricsResponse,
    ServiceStatus,
    StreamConfigUpdate,
    SuccessResponse,
)

__all__ = [
    "ADBDevice",
    "DeviceConnectionOptions",
    "DeviceState",
    "Resolution",
    "TransportType",
    "AudioCodec",
    "ScrcpyConfig",
    "ScrcpyServerState",
    "ScrcpyServerStatus",
    "VideoCodec",
    "AudioFrameData",
    "ControlEvent",
    "ControlEventType",
    "DeviceInfoData",
    "ErrorMessageData",
    "StreamStatusData",
    "VideoFrameData",
    "WSMessage",
    "WSMessageType",
    "DeviceStats",
    "ErrorResponse",
    "HealthCheckResponse",
    "MemoryUsage",
    "MetricsResponse",
    "ServiceStatus",
    "StreamConfigUpdate",
    "SuccessResponse",
]
