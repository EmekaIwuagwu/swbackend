"""
SCRCpy configuration builder
"""

from typing import List

from scws.config import settings
from scws.models import ScrcpyConfig


class ScrcpyConfigBuilder:
    """Build SCRCpy server arguments from configuration"""

    @staticmethod
    def build_args(config: ScrcpyConfig) -> List[str]:
        """Build command line arguments for scrcpy-server"""
        args: List[str] = []

        # Version marker
        args.append("scid=0")

        # Video settings
        args.append(f"max_size={config.max_size}")
        args.append(f"bit_rate={config.bit_rate}")
        args.append(f"max_fps={config.max_fps}")
        args.append(f"video_codec={config.video_codec.value}")

        # Audio settings
        if config.audio:
            args.append("audio=true")
            args.append(f"audio_codec={config.audio_codec.value}")
            args.append(f"audio_bit_rate={config.audio_bit_rate}")
        else:
            args.append("audio=false")

        # Control
        args.append(f"control={str(config.control).lower()}")

        # Optional settings
        if config.display_id is not None:
            args.append(f"display_id={config.display_id}")

        if config.crop:
            args.append(f"crop={config.crop}")

        if config.lock_video_orientation is not None:
            args.append(f"lock_video_orientation={config.lock_video_orientation}")

        if config.tunnel_forward:
            args.append("tunnel_forward=true")

        # Additional settings for reliability
        args.extend([
            "send_device_meta=true",
            "send_frame_meta=true",
            "send_codec_meta=true",
            "send_dummy_byte=false",
            "downsize_on_error=false",
            "cleanup=true",
            "power_off_on_close=false",
        ])

        return args

    @staticmethod
    def build_command(config: ScrcpyConfig) -> str:
        """Build complete server command"""
        args = ScrcpyConfigBuilder.build_args(config)
        server_path = settings.scrcpy_server_path
        return f"CLASSPATH={server_path} app_process / com.genymobile.scrcpy.Server {' '.join(args)}"

    @staticmethod
    def get_server_path() -> str:
        """Get server path from settings"""
        return settings.scrcpy_server_path

    @staticmethod
    def get_server_version() -> str:
        """Get server version from settings"""
        return settings.scrcpy_server_version
