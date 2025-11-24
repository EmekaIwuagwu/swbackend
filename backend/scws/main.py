"""
FastAPI application entry point
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from scws.api import devices, streaming, health
from scws.config import settings
from scws.core.adb import device_manager
from scws.utils import setup_logging, logger
from scws.ws import websocket_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager"""
    # Startup
    setup_logging()
    logger.info("Starting SCWS application", env=settings.env)

    try:
        await device_manager.initialize()
        logger.info("Application started successfully")
        yield
    finally:
        # Shutdown
        logger.info("Shutting down SCWS application")
        await device_manager.shutdown()
        logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="SCWS API",
    description="SCRCpy via WebSockets - Production-grade Android device streaming",
    version="1.0.0",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(devices.router, prefix="/api/devices", tags=["devices"])
app.include_router(streaming.router, prefix="/api/devices", tags=["streaming"])
app.include_router(websocket_router, prefix="/ws", tags=["websocket"])


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint"""
    return {"message": "SCWS API", "version": "1.0.0"}


def main() -> None:
    """Main entry point"""
    import uvicorn

    uvicorn.run(
        "scws.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload and settings.is_development,
        log_config=None,  # Use our custom logging
    )


if __name__ == "__main__":
    main()
