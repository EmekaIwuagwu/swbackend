# SCWS - SCRCpy via WebSockets

[![CI](https://github.com/your-org/scws-v2/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/scws-v2/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **Production-grade WebSocket streaming system for remote Android device control with video/audio streaming**

SCWS is a high-performance, scalable FastAPI backend that enables real-time Android device screen mirroring and remote control through WebSockets. Built with modern Python practices, it leverages SCRCpy for efficient video/audio streaming and provides a RESTful API for device management.

---

## 🚀 Features

- ✅ **Real-time Video/Audio Streaming** - H264/H265 video with AAC/Opus audio
- ✅ **Remote Device Control** - Touch, keyboard, and system button events
- ✅ **Multi-device Support** - Stream from multiple Android devices simultaneously
- ✅ **WebSocket API** - Low-latency bi-directional communication
- ✅ **REST API** - Complete device management endpoints
- ✅ **Production Ready** - Structured logging, health checks, metrics
- ✅ **Type Safe** - Full type hints with MyPy strict mode
- ✅ **Docker Support** - Multi-stage builds for development and production

---

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/your-org/scws-v2.git
cd scws-v2/backend

# Install dependencies
poetry install

# Create .env file
cp .env.example .env
```

### 2. Download SCRCpy Server

```bash
wget https://github.com/Genymobile/scrcpy/releases/download/v2.6.1/scrcpy-server-v2.6.1 -O /opt/scrcpy-server.jar
```

### 3. Run with Docker Compose

```bash
# Start all services (Redroid emulators + Backend + Redis)
docker-compose -f docker/docker-compose.yml up
```

### 4. Access the API

- **API Documentation**: http://localhost:9001/docs
- **Health Check**: http://localhost:9001/api/health

---

## 📚 API Documentation

### REST Endpoints

```http
# Device Management
GET    /api/devices                     # List devices
POST   /api/devices/{serial}/connect    # Connect device
POST   /api/devices/{serial}/stream/start   # Start streaming

# WebSocket
WS     /ws/stream/{serial}   # Video/audio stream
WS     /ws/control/{serial}  # Control events
```

---

## 🛠️ Development

```bash
cd backend

# Run locally
poetry run uvicorn scws.main:app --reload

# Run tests
poetry run pytest

# Code quality
poetry run black scws tests
poetry run ruff check scws tests
poetry run mypy scws
```

---

## 📦 Project Structure

```
backend/
├── scws/
│   ├── api/          # FastAPI routes
│   ├── core/         # Business logic (ADB, SCRCpy)
│   ├── models/       # Pydantic models
│   ├── utils/        # Utilities
│   ├── ws/           # WebSocket handlers
│   └── main.py       # Application entry
├── tests/
├── pyproject.toml
└── Dockerfile
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Built with ❤️ using Python and FastAPI**
