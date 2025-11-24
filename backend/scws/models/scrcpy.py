"""
SCRCpy-related Pydantic models
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class VideoCodec(str, Enum):
    """Video codec types"""

    H264 = "h264"
    H265 = "h265"


class AudioCodec(str, Enum):
    """Audio codec types"""

    AAC = "aac"
    OPUS = "opus"


class ScrcpyConfig(BaseModel):
    """SCRCpy server configuration"""

    max_size: int = Field(default=1920, description="Maximum video dimension")
    bit_rate: int = Field(default=8000000, description="Video bitrate in bps")
    max_fps: int = Field(default=60, description="Maximum frame rate")
    audio_codec: AudioCodec = Field(default=AudioCodec.OPUS, description="Audio codec")
    audio_bit_rate: int = Field(default=128000, description="Audio bitrate in bps")
    video_codec: VideoCodec = Field(default=VideoCodec.H264, description="Video codec")
    control: bool = Field(default=True, description="Enable remote control")
    audio: bool = Field(default=True, description="Enable audio streaming")
    display_id: Optional[int] = Field(None, description="Display ID for multi-display")
    crop: Optional[str] = Field(None, description="Crop video (width:height:x:y)")
    lock_video_orientation: Optional[int] = Field(
        None, description="Lock video orientation (0-3)"
    )
    tunnel_forward: bool = Field(default=True, description="Tunnel forward connections")

    class Config:
        json_schema_extra = {
            "example": {
                "max_size": 1920,
                "bit_rate": 8000000,
                "max_fps": 60,
                "audio_codec": "opus",
                "audio_bit_rate": 128000,
                "video_codec": "h264",
                "control": True,
                "audio": True,
                "tunnel_forward": True,
            }
        }


class ScrcpyServerState(str, Enum):
    """SCRCpy server state"""

    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class ScrcpyServerStatus(BaseModel):
    """SCRCpy server status"""

    state: ScrcpyServerState = Field(..., description="Current server state")
    device_serial: str = Field(..., description="Device serial number")
    config: ScrcpyConfig = Field(..., description="Server configuration")
    start_time: Optional[datetime] = Field(None, description="Start timestamp")
    error: Optional[str] = Field(None, description="Error message if state is error")
