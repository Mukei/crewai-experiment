"""Logging configuration for the application."""
import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys

# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent.parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Log file paths
MAIN_LOG = LOGS_DIR / "main.log"
ERROR_LOG = LOGS_DIR / "error.log"
WEB_SEARCH_LOG = LOGS_DIR / "web_search.log"
CREW_LOG = LOGS_DIR / "crew.log"

# Maximum log file size (5MB) and backup count
MAX_BYTES = 5 * 1024 * 1024
BACKUP_COUNT = 5

def setup_logger(name: str, log_file: Path, level=logging.INFO) -> logging.Logger:
    """Set up a logger with both file and console handlers.
    
    Args:
        name: Logger name
        log_file: Path to log file
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding='utf-8'
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger

# Set up main application logger
main_logger = setup_logger('crewai_experiment', MAIN_LOG)

# Set up error logger with higher level
error_logger = setup_logger('crewai_experiment.error', ERROR_LOG, level=logging.ERROR)

# Set up web search logger
web_search_logger = setup_logger('crewai_experiment.web_search', WEB_SEARCH_LOG)

# Set up crew logger
crew_logger = setup_logger('crewai_experiment.crew', CREW_LOG)

def get_logger(name: str) -> logging.Logger:
    """Get a logger by name.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name) 