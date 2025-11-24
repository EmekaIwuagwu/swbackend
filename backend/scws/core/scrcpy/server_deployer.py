"""
SCRCpy server deployer
Handles deploying scrcpy-server to Android devices
"""

import os
from pathlib import Path

from scws.core.adb import ADBConnection
from scws.utils import ScrcpyDeployError, get_logger

from .config_builder import ScrcpyConfigBuilder

logger = get_logger(__name__)


class ScrcpyServerDeployer:
    """Deploy scrcpy-server to Android devices"""

    SERVER_REMOTE_PATH = "/data/local/tmp/scrcpy-server.jar"

    @classmethod
    async def deploy(cls, connection: ADBConnection) -> None:
        """Deploy scrcpy-server to device"""
        serial = connection.serial

        try:
            logger.info("Deploying scrcpy-server to device", serial=serial)

            server_path = ScrcpyConfigBuilder.get_server_path()

            # Check if server file exists locally
            if not os.path.exists(server_path):
                raise ScrcpyDeployError(
                    f"SCRCpy server file not found at {server_path}. "
                    "Please ensure scrcpy-server.jar is available."
                )

            # Check if server is already deployed
            is_deployed = await cls._is_server_deployed(connection)
            if is_deployed:
                logger.info("SCRCpy server already deployed", serial=serial)
                return

            # Push server to device
            await cls._push_server(connection, server_path)

            # Verify deployment
            verified = await cls._verify_deployment(connection)
            if not verified:
                raise ScrcpyDeployError("Failed to verify scrcpy-server deployment")

            logger.info("SCRCpy server deployed successfully", serial=serial)

        except Exception as e:
            logger.error("Failed to deploy scrcpy-server", serial=serial, error=str(e))
            if isinstance(e, ScrcpyDeployError):
                raise
            raise ScrcpyDeployError("Failed to deploy scrcpy-server", details=str(e))

    @classmethod
    async def _is_server_deployed(cls, connection: ADBConnection) -> bool:
        """Check if server is already deployed"""
        try:
            result = await connection.shell(f"test -f {cls.SERVER_REMOTE_PATH} && echo exists")
            return result.strip() == "exists"
        except Exception:
            return False

    @classmethod
    async def _push_server(cls, connection: ADBConnection, local_path: str) -> None:
        """Push server to device"""
        try:
            logger.debug("Pushing server file", serial=connection.serial, local_path=local_path)
            await connection.push(local_path, cls.SERVER_REMOTE_PATH)
            await connection.shell(f"chmod 644 {cls.SERVER_REMOTE_PATH}")
            logger.debug("Server file pushed successfully", serial=connection.serial)
        except Exception as e:
            raise ScrcpyDeployError("Failed to push server file", details=str(e))

    @classmethod
    async def _verify_deployment(cls, connection: ADBConnection) -> bool:
        """Verify server deployment"""
        try:
            # Check file exists and is a valid JAR
            result = await connection.shell(
                f"file {cls.SERVER_REMOTE_PATH} | grep -q 'Java' && echo valid"
            )
            return result.strip() == "valid"
        except Exception:
            # If file command not available, just check existence
            return await cls._is_server_deployed(connection)

    @classmethod
    async def remove(cls, connection: ADBConnection) -> None:
        """Remove server from device"""
        try:
            logger.info("Removing scrcpy-server from device", serial=connection.serial)
            await connection.shell(f"rm -f {cls.SERVER_REMOTE_PATH}")
            logger.info("SCRCpy server removed", serial=connection.serial)
        except Exception as e:
            logger.error(
                "Failed to remove scrcpy-server", serial=connection.serial, error=str(e)
            )
            raise

    @classmethod
    def get_remote_path(cls) -> str:
        """Get remote server path"""
        return cls.SERVER_REMOTE_PATH
