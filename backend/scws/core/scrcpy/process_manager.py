"""
SCRCpy process manager
Manages scrcpy-server process lifecycle
"""

import asyncio
from datetime import datetime
from typing import Optional

from scws.core.adb import ADBConnection
from scws.models import ScrcpyConfig, ScrcpyServerState, ScrcpyServerStatus
from scws.utils import ScrcpyStartError, ScrcpyServerCrashError, get_logger

from .config_builder import ScrcpyConfigBuilder
from .server_deployer import ScrcpyServerDeployer

logger = get_logger(__name__)


class ScrcpyProcessManager:
    """Manage scrcpy-server process lifecycle"""

    def __init__(self, connection: ADBConnection, config: ScrcpyConfig) -> None:
        self.connection = connection
        self.config = config
        self.state = ScrcpyServerState.STOPPED
        self.start_time: Optional[datetime] = None
        self.error: Optional[str] = None
        self._process_task: Optional[asyncio.Task[None]] = None

    @property
    def serial(self) -> str:
        """Get device serial"""
        return self.connection.serial

    def get_status(self) -> ScrcpyServerStatus:
        """Get current status"""
        return ScrcpyServerStatus(
            state=self.state,
            device_serial=self.serial,
            config=self.config,
            start_time=self.start_time,
            error=self.error,
        )

    def is_running(self) -> bool:
        """Check if server is running"""
        return self.state == ScrcpyServerState.RUNNING

    async def start(self) -> None:
        """Start scrcpy server"""
        if self.state == ScrcpyServerState.RUNNING:
            logger.warning("SCRCpy server already running", serial=self.serial)
            return

        try:
            logger.info("Starting scrcpy server", serial=self.serial)

            self.state = ScrcpyServerState.STARTING
            self.error = None

            # Deploy server if needed
            await ScrcpyServerDeployer.deploy(self.connection)

            # Start server process
            await self._start_process()

            self.state = ScrcpyServerState.RUNNING
            self.start_time = datetime.now()

            logger.info("SCRCpy server started successfully", serial=self.serial)

        except Exception as e:
            self.state = ScrcpyServerState.ERROR
            self.error = str(e)

            logger.error("Failed to start scrcpy server", serial=self.serial, error=str(e))

            await self._cleanup()

            if isinstance(e, ScrcpyStartError):
                raise
            raise ScrcpyStartError(str(e), details=str(e))

    async def stop(self) -> None:
        """Stop scrcpy server"""
        if self.state == ScrcpyServerState.STOPPED:
            return

        logger.info("Stopping scrcpy server", serial=self.serial)

        self.state = ScrcpyServerState.STOPPING

        await self._cleanup()

        self.state = ScrcpyServerState.STOPPED
        self.start_time = None

        logger.info("SCRCpy server stopped", serial=self.serial)

    async def restart(self) -> None:
        """Restart scrcpy server"""
        logger.info("Restarting scrcpy server", serial=self.serial)
        await self.stop()
        await self.start()

    async def _start_process(self) -> None:
        """Start the scrcpy server process"""
        command = ScrcpyConfigBuilder.build_command(self.config)

        logger.debug("Executing scrcpy command", serial=self.serial, command=command)

        try:
            # In a real implementation, you would:
            # 1. Execute the shell command in background
            # 2. Set up socket forwarding for video/audio/control
            # 3. Monitor the process output
            #
            # For now, this is a simplified placeholder
            # You would use asyncio subprocess or connection.shell with proper handling

            # Start server process in background
            # This is a simplified version - production would handle streams properly
            self._process_task = asyncio.create_task(
                self._run_server_process(command)
            )

        except Exception as e:
            raise ScrcpyStartError("Failed to start scrcpy process", details=str(e))

    async def _run_server_process(self, command: str) -> None:
        """Run server process and monitor it"""
        try:
            # Execute command
            # In production, you'd properly handle stdin/stdout/stderr
            await self.connection.shell(command)
        except Exception as e:
            logger.error("SCRCpy server process error", serial=self.serial, error=str(e))
            await self._handle_crash(e)

    async def _handle_crash(self, error: Exception) -> None:
        """Handle server crash"""
        logger.error("SCRCpy server crashed", serial=self.serial, error=str(error))

        self.state = ScrcpyServerState.ERROR
        self.error = str(error)

        await self._cleanup()

    async def _cleanup(self) -> None:
        """Cleanup resources"""
        # Cancel process task
        if self._process_task:
            self._process_task.cancel()
            try:
                await self._process_task
            except asyncio.CancelledError:
                pass
            self._process_task = None

        # In production, you would also:
        # - Close socket connections
        # - Remove port forwards
        # - Kill the server process if still running

        logger.debug("Cleanup completed", serial=self.serial)
