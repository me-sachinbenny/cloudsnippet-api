"""
Logging Configuration

This module implements a custom logger with colored console output and file storage.
"""

import os
import sys
import logging
import uuid
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from datetime import datetime

from .config import Settings

# Load settings
settings = Settings()

# Define ANSI color codes for log levels
COLORS = {
    'DEBUG': '\033[94m',  # Blue
    'INFO': '\033[92m',   # Green
    'WARNING': '\033[93m', # Yellow
    'ERROR': '\033[91m',   # Red
    'CRITICAL': '\033[91m\033[1m', # Bold Red
    'RESET': '\033[0m'    # Reset to default color
}

# Ensure logs directory exists
LOG_DIR = Path(settings.LOG_DIR)
LOG_DIR.mkdir(exist_ok=True)

class ColoredFormatter(logging.Formatter):
    """
    Custom formatter to add colors to log messages in the console.
    """
    
    def format(self, record):
        level_name = record.levelname
        message = super().format(record)
        
        # Add color to console output only (not for file logging)
        if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
            color = COLORS.get(level_name, COLORS['RESET'])
            message = f"{color}{message}{COLORS['RESET']}"
            
        return message

def get_logger(name, log_level=None, log_to_file=None):
    """
    Create a logger with both console and file handlers.
    """
    # Use settings from config if not explicitly provided
    log_level = log_level if log_level is not None else settings.log_level
    log_to_file = log_to_file if log_to_file is not None else settings.LOG_TO_FILE
    
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Clear existing handlers if any
    if logger.handlers:
        logger.handlers.clear()
    
    # Console handler with colored output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_format = '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
    console_formatter = ColoredFormatter(console_format, datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_to_file:
        # Daily rotating file handler
        log_file = LOG_DIR / f"{name}.log"
        file_handler = TimedRotatingFileHandler(
            filename=log_file,
            when='midnight',
            backupCount=14  # Keep logs for 14 days
        )
        file_handler.setLevel(log_level)
        file_format = '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s | %(pathname)s:%(lineno)d'
        file_formatter = logging.Formatter(file_format, datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Also create a separate error log file for ERROR and CRITICAL logs
        error_file = LOG_DIR / f"{name}_error.log"
        error_handler = RotatingFileHandler(
            filename=error_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        logger.addHandler(error_handler)
    
    return logger

# Default application logger
app_logger = get_logger("cloudsnippet_api")

class LoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter to add context information to log messages.
    """
    def process(self, msg, kwargs):
        # Add request ID if available
        if hasattr(self.extra, 'request_id'):
            return f"[RequestID: {self.extra.request_id}] {msg}", kwargs
        return msg, kwargs

def get_request_logger(request_id=None):
    """
    Get a logger configured specifically for a request with request ID context.
    """
    if request_id is None:
        request_id = str(uuid.uuid4())
        
    logger = app_logger
    extra = type('obj', (object,), {'request_id': request_id})
    return LoggerAdapter(logger, extra)