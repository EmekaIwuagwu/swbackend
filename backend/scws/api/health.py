"""
Health check and metrics endpoints
"""

import time
from datetime import datetime

import psutil
from fastapi import APIRouter

from scws.core.adb import device_manager
from scws.models import HealthCheckResponse, MetricsResponse, MemoryUsage, ServiceStatus

router = APIRouter()

# Track startup time
startup_time = time.time()


@router.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """Health check endpoint"""
    uptime = time.time() - startup_time

    # Check ADB daemon connection
    try:
        devices = await device_manager.list_devices()
        adb_status = "connected"
    except Exception:
        adb_status = "disconnected"

    status = "healthy" if adb_status == "connected" else "unhealthy"

    return HealthCheckResponse(
        status=status,
        uptime=uptime,
        timestamp=datetime.now().isoformat(),
        services=ServiceStatus(adb=adb_status),  # type: ignore
    )


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics() -> MetricsResponse:
    """Get application metrics"""
    devices = await device_manager.list_devices()

    # Get system metrics
    cpu_usage = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()

    return MetricsResponse(
        active_devices=len(devices),
        active_streams=0,  # TODO: Implement stream tracking
        total_connections=0,  # TODO: Implement connection tracking
        cpu_usage=cpu_usage,
        memory_usage=MemoryUsage(
            used=memory.used,
            total=memory.total,
            percentage=memory.percent,
        ),
        timestamp=datetime.now().isoformat(),
    )
