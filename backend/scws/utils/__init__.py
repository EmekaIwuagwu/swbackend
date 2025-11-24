"""
Utility modules
"""

from .logger import get_logger, logger, setup_logging
from .errors import (
    AppError,
    ADBConnectionError,
    ADBDeviceNotFoundError,
    ADBDeviceUnauthorizedError,
    ADBDeviceOfflineError,
    ScrcpyDeployError,
    ScrcpyStartError,
    ScrcpyServerCrashError,
    StreamNotFoundError,
    StreamAlreadyActiveError,
    ValidationError,
    NotFoundError,
)

__all__ = [
    "logger",
    "get_logger",
    "setup_logging",
    "AppError",
    "ADBConnectionError",
    "ADBDeviceNotFoundError",
    "ADBDeviceUnauthorizedError",
    "ADBDeviceOfflineError",
    "ScrcpyDeployError",
    "ScrcpyStartError",
    "ScrcpyServerCrashError",
    "StreamNotFoundError",
    "StreamAlreadyActiveError",
    "ValidationError",
    "NotFoundError",
]
