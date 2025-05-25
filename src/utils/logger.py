"""
Logging utility for the Personal Assistant application.
"""

import logging
import os
from datetime import datetime


def setup_logger(name: str = "assistant", level: str = "INFO") -> logging.Logger:
    """
    Set up a logger with file and console handlers.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # File handler
    log_filename = f"logs/assistant_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def log_error(logger: logging.Logger, error: Exception, context: str = ""):
    """
    Log an error with context information.
    
    Args:
        logger: Logger instance
        error: Exception to log
        context: Additional context information
    """
    error_msg = f"{context}: {str(error)}" if context else str(error)
    logger.error(error_msg, exc_info=True)


def log_api_call(logger: logging.Logger, service: str, endpoint: str, status: str):
    """
    Log API call information.
    
    Args:
        logger: Logger instance
        service: Service name (e.g., "OpenWeather", "Ollama")
        endpoint: API endpoint
        status: Call status (success/error)
    """
    logger.info(f"API Call - {service} - {endpoint} - {status}")


# Create default logger
default_logger = setup_logger() 