"""Tests for logging configuration."""
import pytest
import logging
from pathlib import Path
from src.utils.logging_config import (
    setup_logger,
    main_logger,
    crew_logger,
    file_manager_logger,
    progress_tracker_logger,
    ui_logger,
    error_logger,
    LOGS_DIR
)

@pytest.fixture
def temp_log_dir(tmp_path):
    """Create a temporary directory for log files."""
    return tmp_path

def test_logs_directory_creation():
    """Test that logs directory is created."""
    assert LOGS_DIR.exists()
    assert LOGS_DIR.is_dir()

def test_logger_creation(temp_log_dir):
    """Test logger creation with file and console handlers."""
    logger = setup_logger("test", "test.log")
    
    # Check logger configuration
    assert logger.name == "test"
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 2
    
    # Check handler types
    handlers = logger.handlers
    assert any(isinstance(h, logging.FileHandler) for h in handlers)
    assert any(isinstance(h, logging.StreamHandler) for h in handlers)

def test_logger_duplicate_handlers():
    """Test that duplicate handlers are not added."""
    logger_name = "test_duplicate"
    
    # Create logger twice
    logger1 = setup_logger(logger_name, "test.log")
    logger2 = setup_logger(logger_name, "test.log")
    
    # Should be the same logger with same handlers
    assert logger1 is logger2
    assert len(logger1.handlers) == 2

def test_error_logger_level():
    """Test that error logger has correct level."""
    assert error_logger.level == logging.ERROR

def test_dedicated_loggers():
    """Test that all dedicated loggers are created correctly."""
    loggers = [
        main_logger,
        crew_logger,
        file_manager_logger,
        progress_tracker_logger,
        ui_logger,
        error_logger
    ]
    
    for logger in loggers:
        assert isinstance(logger, logging.Logger)
        assert len(logger.handlers) == 2
        assert logger.name in [
            "main",
            "crew",
            "file_manager",
            "progress_tracker",
            "ui",
            "error"
        ]

def test_log_file_creation():
    """Test that log files are created when logging."""
    # Log a message to each logger
    test_message = "Test log message"
    loggers = [
        main_logger,
        crew_logger,
        file_manager_logger,
        progress_tracker_logger,
        ui_logger,
        error_logger
    ]
    
    for logger in loggers:
        logger.info(test_message)
        log_file = LOGS_DIR / f"{logger.name}.log"
        assert log_file.exists()
        
        # Check message in file
        content = log_file.read_text()
        assert test_message in content

def test_logger_formatting():
    """Test logger formatting."""
    test_logger = setup_logger("format_test", "format_test.log")
    test_message = "Test format message"
    
    # Log a message
    test_logger.info(test_message)
    
    # Check file handler format
    log_file = LOGS_DIR / "format_test.log"
    content = log_file.read_text()
    assert test_message in content
    assert " - format_test - INFO - " in content 