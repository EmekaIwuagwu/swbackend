"""
Application configuration using Pydantic Settings
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Server Configuration
    env: Literal["development", "production", "test"] = Field(default="development")
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=9001)
    reload: bool = Field(default=False)

    # ADB Configuration
    adb_host: str = Field(default="127.0.0.1")
    adb_port: int = Field(default=5037)

    # SCRCpy Configuration
    scrcpy_server_version: str = Field(default="2.6.1")
    scrcpy_server_path: str = Field(default="/opt/scrcpy-server.jar")
    scrcpy_max_size: int = Field(default=1920)
    scrcpy_bit_rate: int = Field(default=8000000)
    scrcpy_max_fps: int = Field(default=60)

    # WebSocket Configuration
    ws_max_connections: int = Field(default=100)
    ws_heartbeat_interval: int = Field(default=30)

    # Redis Configuration
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_db: int = Field(default=0)
    redis_password: str | None = Field(default=None)

    # Logging Configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(default="INFO")
    log_format: Literal["json", "console"] = Field(default="console")

    # Monitoring
    enable_metrics: bool = Field(default=True)
    metrics_port: int = Field(default=9090)

    # CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"]
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from comma-separated string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.env == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.env == "production"

    @property
    def is_test(self) -> bool:
        """Check if running in test mode"""
        return self.env == "test"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
