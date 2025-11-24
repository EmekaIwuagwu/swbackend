"""
REST API request/response models
"""

from typing import Any, Generic, Literal, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorResponse(BaseModel):
    """Standard error response"""

    class ErrorDetail(BaseModel):
        code: str = Field(..., description="Error code")
        message: str = Field(..., description="Human-readable error message")
        details: Optional[Any] = Field(None, description="Additional error details")
        timestamp: str = Field(..., description="Timestamp when error occurred")
        request_id: str = Field(..., description="Request ID for tracing")

    error: ErrorDetail


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response wrapper"""

    data: T = Field(..., description="Response data")
    timestamp: str = Field(..., description="Response timestamp")
    request_id: str = Field(..., description="Request ID")


class ServiceStatus(BaseModel):
    """Service status"""

    adb: Literal["connected", "disconnected"] = Field(..., description="ADB daemon status")
    redis: Optional[Literal["connected", "disconnected"]] = Field(
        None, description="Redis status"
    )


class HealthCheckResponse(BaseModel):
    """Health check response"""

    status: Literal["healthy", "unhealthy"] = Field(..., description="Overall health status")
    uptime: float = Field(..., description="Uptime in seconds")
    timestamp: str = Field(..., description="Current timestamp")
    services: ServiceStatus = Field(..., description="Service statuses")


class MemoryUsage(BaseModel):
    """Memory usage information"""

    used: int = Field(..., description="Used memory in bytes")
    total: int = Field(..., description="Total memory in bytes")
    percentage: float = Field(..., description="Usage percentage")


class MetricsResponse(BaseModel):
    """Metrics response"""

    active_devices: int = Field(..., description="Number of active devices")
    active_streams: int = Field(..., description="Number of active streams")
    total_connections: int = Field(..., description="Total WebSocket connections")
    cpu_usage: float = Field(..., description="CPU usage percentage")
    memory_usage: MemoryUsage = Field(..., description="Memory usage")
    timestamp: str = Field(..., description="Metrics timestamp")


class DeviceStats(BaseModel):
    """Device streaming statistics"""

    serial: str = Field(..., description="Device serial")
    stream_duration: float = Field(..., description="Stream duration in seconds")
    video_frames_processed: int = Field(..., description="Total video frames processed")
    audio_frames_processed: int = Field(..., description="Total audio frames processed")
    control_events_processed: int = Field(..., description="Total control events processed")
    current_fps: float = Field(..., description="Current frame rate")
    average_fps: float = Field(..., description="Average frame rate")
    video_bitrate: int = Field(..., description="Video bitrate")
    audio_bitrate: int = Field(..., description="Audio bitrate")
    network_latency: float = Field(..., description="Network latency in ms")
    timestamp: str = Field(..., description="Stats timestamp")


class StreamConfigUpdate(BaseModel):
    """Stream configuration update request"""

    max_size: Optional[int] = Field(None, description="Maximum video dimension")
    bit_rate: Optional[int] = Field(None, description="Video bitrate")
    max_fps: Optional[int] = Field(None, description="Maximum frame rate")
    audio_codec: Optional[Literal["aac", "opus"]] = Field(None, description="Audio codec")
    audio_bit_rate: Optional[int] = Field(None, description="Audio bitrate")
    video_codec: Optional[Literal["h264", "h265"]] = Field(None, description="Video codec")
