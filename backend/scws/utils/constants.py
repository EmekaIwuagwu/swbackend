"""
Application constants
"""

# Android key codes (subset of commonly used keys)
ANDROID_KEY_CODES = {
    "KEYCODE_HOME": 3,
    "KEYCODE_BACK": 4,
    "KEYCODE_MENU": 82,
    "KEYCODE_POWER": 26,
    "KEYCODE_VOLUME_UP": 24,
    "KEYCODE_VOLUME_DOWN": 25,
    "KEYCODE_ENTER": 66,
    "KEYCODE_DEL": 67,
    "KEYCODE_SPACE": 62,
}

# Performance targets
PERFORMANCE_TARGETS = {
    "TARGET_VIDEO_LATENCY_MS": 50,
    "MAX_VIDEO_LATENCY_MS": 100,
    "TARGET_CONTROL_LATENCY_MS": 20,
    "MAX_CONTROL_LATENCY_MS": 30,
    "MIN_FPS": 30,
    "TARGET_FPS": 60,
}

# Timeouts
TIMEOUTS = {
    "ADB_CONNECTION_TIMEOUT": 30,  # seconds
    "SCRCPY_START_TIMEOUT": 10,  # seconds
    "WEBSOCKET_PING_TIMEOUT": 30,  # seconds
}

# Limits
LIMITS = {
    "MAX_CONCURRENT_STREAMS": 10,
    "MAX_CLIENTS_PER_DEVICE": 5,
    "MAX_FRAME_BUFFER_SIZE": 100,
}
