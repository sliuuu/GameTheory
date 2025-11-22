"""
Utility module for managing persistent storage paths.
Centralizes path configuration for cache, logs, outputs, state, and API history.
"""

import os
from pathlib import Path


def get_cache_dir():
    """Get the cache directory path."""
    return Path(os.getenv("CACHE_DIR", ".market_data_cache"))


def get_log_dir():
    """Get the logs directory path."""
    log_dir = Path(os.getenv("LOG_DIR", "data/logs"))
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def get_output_dir():
    """Get the model outputs directory path."""
    output_dir = Path(os.getenv("OUTPUT_DIR", "data/outputs"))
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def get_state_dir():
    """Get the application state directory path."""
    state_dir = Path(os.getenv("STATE_DIR", "data/state"))
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir


def get_api_history_dir():
    """Get the API history directory path."""
    api_dir = Path(os.getenv("API_HISTORY_DIR", "data/api_history"))
    api_dir.mkdir(parents=True, exist_ok=True)
    return api_dir


def get_backend_log_file():
    """Get the backend log file path."""
    log_dir = get_log_dir()
    return log_dir / "backend.log"


def get_frontend_log_file():
    """Get the frontend log file path."""
    log_dir = get_log_dir()
    return log_dir / "frontend" / "frontend.log"


def ensure_directories():
    """Ensure all required directories exist."""
    get_cache_dir().mkdir(parents=True, exist_ok=True)
    get_log_dir().mkdir(parents=True, exist_ok=True)
    get_output_dir().mkdir(parents=True, exist_ok=True)
    get_state_dir().mkdir(parents=True, exist_ok=True)
    get_api_history_dir().mkdir(parents=True, exist_ok=True)
    (get_log_dir() / "frontend").mkdir(parents=True, exist_ok=True)

