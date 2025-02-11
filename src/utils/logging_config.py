"""Logging configuration for the application."""
import logging
import sys
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Common log format with ISO timestamp
LOG_FORMAT = "%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logger(name: str, log_file: str, level: int = logging.INFO) -> logging.Logger:
    """Set up a logger with file and console handlers.
    
    Args:
        name: Logger name
        log_file: Log file path
        level: Logging level
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers = []
    
    # File handler with ISO timestamp
    file_handler = logging.FileHandler(LOGS_DIR / log_file, mode='a')
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    logger.addHandler(file_handler)
    
    # Console handler with simpler format
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger by name. If it doesn't exist, create it with default settings.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name, f"{name}.log")
    return logger

# Create dedicated loggers
main_logger = setup_logger("main", "main.log")
crew_logger = setup_logger("crew", "crew.log")
file_manager_logger = setup_logger("file_manager", "file_manager.log")
progress_tracker_logger = setup_logger("progress_tracker", "progress_tracker.log")
ui_logger = setup_logger("ui", "ui.log")
error_logger = setup_logger("error", "error.log", level=logging.ERROR)
web_search_logger = setup_logger("web_search", "web_search.log")

# Log startup with timestamp
startup_msg = f"Logging system initialized at {datetime.now().isoformat()}"
main_logger.info(startup_msg)

# Ensure all log files are created
for logger_name in ["main", "crew", "file_manager", "progress_tracker", "ui", "error", "web_search"]:
    log_file = LOGS_DIR / f"{logger_name}.log"
    if not log_file.exists():
        log_file.touch()
        main_logger.info(f"Created log file: {log_file}") 