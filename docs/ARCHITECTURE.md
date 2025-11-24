# SCWS Architecture Documentation

## Overview

SCWS (SCRCpy via WebSockets) is a production-grade FastAPI backend system that provides real-time Android device screen mirroring and remote control capabilities through WebSockets.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Layer                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │  Browser │  │  Mobile  │  │ Desktop  │                 │
│  │   App    │  │   App    │  │   App    │                 │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                 │
└───────┼─────────────┼─────────────┼────────────────────────┘
        │             │             │
        │ HTTP/WS     │ HTTP/WS     │ HTTP/WS
        ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 9001)                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ REST API Layer                                       │  │
│  │  - Device Management (/api/devices)                  │  │
│  │  - Streaming Control (/api/devices/{}/stream)       │  │
│  │  - Health & Metrics (/api/health, /api/metrics)     │  │
│  └────────────────────┬─────────────────────────────────┘  │
│  ┌────────────────────┴─────────────────────────────────┐  │
│  │ WebSocket Layer                                      │  │
│  │  - Video/Audio Streaming (/ws/stream/{serial})      │  │
│  │  - Control Events (/ws/control/{serial})            │  │
│  └────────────────────┬─────────────────────────────────┘  │
│  ┌────────────────────┴─────────────────────────────────┐  │
│  │ Business Logic Layer                                 │  │
│  │  ┌──────────────┐  ┌──────────────┐                 │  │
│  │  │ ADB Manager  │  │ SCRCpy Mgr   │                 │  │
│  │  │ - Connection │  │ - Deploy     │                 │  │
│  │  │ - Discovery  │  │ - Lifecycle  │                 │  │
│  │  └──────────────┘  └──────────────┘                 │  │
│  └────────────────────┬─────────────────────────────────┘  │
└───────────────────────┼──────────────────────────────────────┘
                        │ ADB Protocol
                        ▼
          ┌─────────────────────────────┐
          │    Android Devices          │
          │  - Physical (USB/WiFi)      │
          │  - Emulators (Redroid)      │
          └─────────────────────────────┘
```

## Core Components

### 1. FastAPI Application (`scws/main.py`)

- Entry point for the application
- Configures CORS, middleware, and routers
- Implements application lifespan management
- Initializes device manager on startup

### 2. Device Management (`scws/core/adb/`)

**ADBConnection** (`connection.py`)
- Manages individual device connections using adb-shell
- Handles connection lifecycle (connect, disconnect, health check)
- Provides shell command execution
- Supports file push/pull operations
- Retrieves device information

**ADBDeviceManager** (`device_manager.py`)
- Singleton service managing all device connections
- Implements device discovery and polling
- Maintains connection pool
- Handles device lifecycle events
- Performs periodic health checks

### 3. SCRCpy Integration (`scws/core/scrcpy/`)

**ScrcpyConfigBuilder** (`config_builder.py`)
- Builds SCRCpy server command-line arguments
- Validates and merges configuration
- Manages server parameters (video, audio, control)

**ScrcpyServerDeployer** (`server_deployer.py`)
- Deploys scrcpy-server.jar to Android devices
- Verifies deployment success
- Manages server file lifecycle
- Handles deployment errors

**ScrcpyProcessManager** (`process_manager.py`)
- Manages scrcpy-server process lifecycle
- Handles server start/stop/restart operations
- Monitors server health and crash detection
- Manages video/audio/control sockets

### 4. API Layer (`scws/api/`)

**Device API** (`devices.py`)
- `GET /api/devices` - List all connected devices
- `GET /api/devices/{serial}` - Get device information
- `POST /api/devices/{serial}/connect` - Connect to device
- `DELETE /api/devices/{serial}/disconnect` - Disconnect device

**Streaming API** (`streaming.py`)
- `POST /api/devices/{serial}/stream/start` - Start streaming
- `POST /api/devices/{serial}/stream/stop` - Stop streaming
- `GET /api/devices/{serial}/stream/status` - Get stream status
- `PATCH /api/devices/{serial}/stream/config` - Update configuration

**Health API** (`health.py`)
- `GET /api/health` - Service health check
- `GET /api/metrics` - Application metrics (CPU, memory, devices)

### 5. WebSocket Layer (`scws/ws/`)

**ConnectionManager** (`router.py`)
- Manages WebSocket connection lifecycle
- Broadcasts messages to connected clients
- Handles client disconnections
- Implements per-device connection pools

**WebSocket Endpoints**
- `/ws/stream/{serial}` - Video/audio streaming endpoint
- `/ws/control/{serial}` - Control events endpoint

### 6. Data Models (`scws/models/`)

**Pydantic Models**
- `device.py` - ADBDevice, DeviceState, TransportType
- `scrcpy.py` - ScrcpyConfig, ScrcpyServerStatus
- `websocket.py` - WSMessage, ControlEvent, VideoFrameData, AudioFrameData
- `api.py` - Request/response schemas

### 7. Utilities (`scws/utils/`)

**Logger** (`logger.py`)
- Structured logging with structlog
- Configurable JSON/console output
- Log levels and formatting

**Errors** (`errors.py`)
- Custom exception hierarchy
- HTTP status code mapping
- Error serialization

**Async Helpers** (`async_helpers.py`)
- Retry with exponential backoff
- Timeout utilities

## Data Flow

### Device Connection Flow

```
Client Request → REST API → Device Manager → ADB Connection
                                ↓
                        Device Info Retrieved
                                ↓
                        Connection Stored
                                ↓
                        Response to Client
```

### Streaming Start Flow

```
Client Request → REST API → Get/Create ADB Connection
                                ↓
                        Deploy SCRCpy Server
                                ↓
                        Start SCRCpy Process
                                ↓
                        Create Process Manager
                                ↓
                        Response to Client
```

### WebSocket Streaming Flow

```
Client Connects → WebSocket Handler → Connection Manager
                                          ↓
                                    Send Device Info
                                          ↓
                          ┌───────────────┴────────────────┐
                          ▼                                ▼
                    Video/Audio Stream              Control Events
                          │                                │
                          ▼                                ▼
                    Broadcast to Clients         Process on Device
```

## Key Design Patterns

### 1. Singleton Pattern
- **ADBDeviceManager**: Single instance manages all device connections

### 2. Manager Pattern
- **ConnectionManager**: Manages WebSocket connections per device
- **ScrcpyProcessManager**: Manages scrcpy server lifecycle per device

### 3. Repository Pattern
- Device manager maintains device connection pool
- Stream manager maintains active stream sessions

### 4. Observer Pattern
- WebSocket clients subscribe to device streams
- Connection manager broadcasts to all subscribers

### 5. Dependency Injection
- FastAPI's dependency injection for configuration
- Singleton services injected into route handlers

## Configuration Management

### Environment-based Configuration
- Pydantic Settings for type-safe configuration
- Support for `.env` files
- Environment variable validation
- Sensible defaults

### Configuration Layers
1. Default values in code
2. `.env` file overrides
3. Environment variable overrides
4. Runtime configuration updates

## Error Handling Strategy

### Error Hierarchy
```
AppError (base)
├── ADBConnectionError
├── ADBDeviceNotFoundError
├── ADBDeviceUnauthorizedError
├── ADBDeviceOfflineError
├── ScrcpyDeployError
├── ScrcpyStartError
├── ScrcpyServerCrashError
├── StreamNotFoundError
└── ValidationError
```

### Error Response Format
```json
{
  "code": "ERROR_CODE",
  "message": "Human-readable message",
  "details": {},
  "timestamp": "2024-01-01T12:00:00Z",
  "request_id": "uuid"
}
```

## Performance Considerations

### Connection Pooling
- Reuse existing ADB connections
- Connection health monitoring
- Automatic reconnection on failure

### Asynchronous Operations
- FastAPI async/await throughout
- Non-blocking I/O operations
- Concurrent device handling

### Resource Management
- Automatic cleanup on shutdown
- Process lifecycle management
- WebSocket connection limits

## Security Considerations

### Authentication (Future)
- JWT token-based authentication
- API key authentication
- Role-based access control

### Device Security
- ADB key pair authentication
- Device authorization required
- Secure WebSocket connections (WSS)

### Input Validation
- Pydantic model validation
- SQL injection prevention
- Command injection prevention

## Monitoring & Observability

### Structured Logging
- Contextual logging with structlog
- JSON output for production
- Console output for development

### Metrics
- Active device count
- Active stream count
- CPU and memory usage
- Request latency (future)

### Health Checks
- ADB daemon connectivity
- Redis connectivity
- Service uptime

## Scalability

### Horizontal Scaling
- Stateless API design
- Redis for session sharing
- Load balancer compatible

### Vertical Scaling
- Async I/O for efficient resource usage
- Connection pooling
- Process-per-device isolation

## Deployment

### Docker
- Multi-stage builds for optimization
- Development and production Dockerfiles
- Docker Compose for local development

### Environment Support
- Development (auto-reload, debug logging)
- Production (optimized, JSON logging)
- Testing (isolated environment)

## Future Enhancements

1. **Video/Audio Processing**
   - Transcoding support
   - Adaptive bitrate
   - Frame buffer management

2. **Control Events**
   - Multi-touch support
   - Gesture recognition
   - Clipboard sync

3. **Security**
   - OAuth2 authentication
   - Rate limiting
   - IP whitelisting

4. **Features**
   - Screen recording
   - File transfer UI
   - Device screenshots

5. **Performance**
   - Redis caching
   - CDN integration
   - WebRTC support
