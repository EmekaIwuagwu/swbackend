"""
Device management endpoints
"""

from typing import List

from fastapi import APIRouter, HTTPException

from scws.core.adb import device_manager
from scws.models import ADBDevice
from scws.utils import ADBDeviceNotFoundError, AppError

router = APIRouter()


@router.get("", response_model=List[ADBDevice])
async def list_devices() -> List[ADBDevice]:
    """List all connected devices"""
    try:
        devices = await device_manager.list_devices()
        return devices
    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail=e.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.get("/{serial}", response_model=ADBDevice)
async def get_device(serial: str) -> ADBDevice:
    """Get device information"""
    device = device_manager.get_device(serial)
    if not device:
        raise HTTPException(status_code=404, detail={"error": f"Device not found: {serial}"})
    return device


@router.post("/{serial}/connect", response_model=ADBDevice)
async def connect_device(serial: str) -> ADBDevice:
    """Connect to a device"""
    try:
        connection = await device_manager.connect_to_device(serial)
        device_info = await connection.get_device_info()
        return device_info
    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail=e.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.delete("/{serial}/disconnect")
async def disconnect_device(serial: str) -> dict[str, str]:
    """Disconnect from a device"""
    try:
        await device_manager.disconnect_from_device(serial)
        return {"message": f"Device {serial} disconnected"}
    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail=e.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})
