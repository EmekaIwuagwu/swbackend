"""
Streaming control endpoints
"""

from fastapi import APIRouter, HTTPException

from scws.core.adb import device_manager
from scws.core.scrcpy import ScrcpyProcessManager
from scws.models import ScrcpyConfig, ScrcpyServerStatus, StreamConfigUpdate
from scws.utils import AppError

router = APIRouter()

# Track active streaming sessions
# In production, this would be a proper service/manager
active_streams: dict[str, ScrcpyProcessManager] = {}


@router.post("/{serial}/stream/start", response_model=ScrcpyServerStatus)
async def start_stream(serial: str, config: ScrcpyConfig | None = None) -> ScrcpyServerStatus:
    """Start streaming for a device"""
    try:
        # Get or create connection
        connection = device_manager.get_connection(serial)
        if not connection.is_connected:
            connection = await device_manager.connect_to_device(serial)

        # Check if stream already active
        if serial in active_streams and active_streams[serial].is_running():
            raise HTTPException(
                status_code=409,
                detail={"error": f"Stream already active for device: {serial}"},
            )

        # Create process manager
        stream_config = config or ScrcpyConfig()
        process_manager = ScrcpyProcessManager(connection, stream_config)

        # Start streaming
        await process_manager.start()

        active_streams[serial] = process_manager

        return process_manager.get_status()

    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail=e.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.post("/{serial}/stream/stop")
async def stop_stream(serial: str) -> dict[str, str]:
    """Stop streaming for a device"""
    try:
        process_manager = active_streams.get(serial)
        if not process_manager:
            raise HTTPException(
                status_code=404, detail={"error": f"Stream not found for device: {serial}"}
            )

        await process_manager.stop()
        del active_streams[serial]

        return {"message": f"Stream stopped for device {serial}"}

    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail=e.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.get("/{serial}/stream/status", response_model=ScrcpyServerStatus)
async def get_stream_status(serial: str) -> ScrcpyServerStatus:
    """Get stream status for a device"""
    process_manager = active_streams.get(serial)
    if not process_manager:
        raise HTTPException(
            status_code=404, detail={"error": f"Stream not found for device: {serial}"}
        )

    return process_manager.get_status()


@router.patch("/{serial}/stream/config")
async def update_stream_config(
    serial: str, config_update: StreamConfigUpdate
) -> dict[str, str]:
    """Update stream configuration (requires restart)"""
    try:
        process_manager = active_streams.get(serial)
        if not process_manager:
            raise HTTPException(
                status_code=404, detail={"error": f"Stream not found for device: {serial}"}
            )

        # Update configuration
        current_config = process_manager.config
        updated_config = current_config.model_copy(
            update=config_update.model_dump(exclude_unset=True)
        )

        # Create new process manager with updated config
        connection = device_manager.get_connection(serial)
        new_process_manager = ScrcpyProcessManager(connection, updated_config)

        # Restart with new configuration
        await process_manager.stop()
        await new_process_manager.start()

        active_streams[serial] = new_process_manager

        return {"message": "Stream configuration updated and restarted"}

    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail=e.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})
