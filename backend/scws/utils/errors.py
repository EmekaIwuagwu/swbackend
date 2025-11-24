"""
Custom exception classes
"""

from typing import Any, Optional


class AppError(Exception):
    """Base application error"""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 500,
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary"""
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


# ADB Errors
class ADBConnectionError(AppError):
    """ADB connection error"""

    def __init__(self, message: str, details: Optional[Any] = None) -> None:
        super().__init__("ADB_CONNECTION_FAILED", message, 503, details)


class ADBDeviceNotFoundError(AppError):
    """ADB device not found error"""

    def __init__(self, serial: str) -> None:
        super().__init__(
            "ADB_DEVICE_NOT_FOUND",
            f"Device not found: {serial}",
            404,
            {"serial": serial},
        )


class ADBDeviceUnauthorizedError(AppError):
    """ADB device unauthorized error"""

    def __init__(self, serial: str) -> None:
        super().__init__(
            "ADB_DEVICE_UNAUTHORIZED",
            f"Device unauthorized: {serial}. Please authorize on device.",
            403,
            {"serial": serial},
        )


class ADBDeviceOfflineError(AppError):
    """ADB device offline error"""

    def __init__(self, serial: str) -> None:
        super().__init__(
            "ADB_DEVICE_OFFLINE",
            f"Device offline: {serial}",
            503,
            {"serial": serial},
        )


# SCRCpy Errors
class ScrcpyDeployError(AppError):
    """SCRCpy deploy error"""

    def __init__(self, message: str, details: Optional[Any] = None) -> None:
        super().__init__("SCRCPY_DEPLOY_FAILED", message, 500, details)


class ScrcpyStartError(AppError):
    """SCRCpy start error"""

    def __init__(self, message: str, details: Optional[Any] = None) -> None:
        super().__init__("SCRCPY_START_FAILED", message, 500, details)


class ScrcpyServerCrashError(AppError):
    """SCRCpy server crash error"""

    def __init__(self, message: str, details: Optional[Any] = None) -> None:
        super().__init__("SCRCPY_SERVER_CRASHED", message, 500, details)


# Streaming Errors
class StreamNotFoundError(AppError):
    """Stream not found error"""

    def __init__(self, serial: str) -> None:
        super().__init__(
            "STREAM_NOT_FOUND",
            f"Stream not found for device: {serial}",
            404,
            {"serial": serial},
        )


class StreamAlreadyActiveError(AppError):
    """Stream already active error"""

    def __init__(self, serial: str) -> None:
        super().__init__(
            "STREAM_ALREADY_ACTIVE",
            f"Stream already active for device: {serial}",
            409,
            {"serial": serial},
        )


# Generic Errors
class ValidationError(AppError):
    """Validation error"""

    def __init__(self, message: str, details: Optional[Any] = None) -> None:
        super().__init__("VALIDATION_ERROR", message, 400, details)


class NotFoundError(AppError):
    """Not found error"""

    def __init__(self, resource: str) -> None:
        super().__init__("NOT_FOUND", f"{resource} not found", 404)
