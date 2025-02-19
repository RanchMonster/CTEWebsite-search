"""
LogManager.py - Custom logging module for CTE-Search application

This module provides a custom logging implementation with the following features:
- Daily rotating log files stored in a 'logs' directory
- Asynchronous log file handler updates
- Log level set to DEBUG
- Formatted log messages with timestamp, level, and message
- Global logger instance with convenience methods for different log levels
- Custom error callbacks for handling log messages

The log files are named in the format: logs/cte_search_YYYYMMDD.log

Functions:
    logger_loop() - Initializes and maintains the logger
    update_file_handler() - Updates log file handler when date changes
    info(msg) - Logs an info message
    debug(msg) - Logs a debug message
    warning(msg) - Logs a warning message
    error(msg) - Logs an error message
    critical(msg) - Logs a critical message
    add_error_callback(callback) - Adds a callback function for error handling
"""

from logging import Logger, FileHandler, Formatter
import os
from datetime import datetime
import asyncio
from typing import Callable, List

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Setup logger
__LOGGER = Logger('CTE-Search') # We use caps for constance in python
__LOGGER.setLevel('DEBUG')

# Create formatters and handlers
formatter = Formatter('[%(asctime)s] - %(levelname)s - %(message)s')

# File handler with dynamic name
__current_date = None
__file_handler = None
__ready = False
__error_callbacks: List[Callable[[str], None]] = []

async def update_file_handler():
    """Periodically updates the log file handler when the date changes."""
    global __current_date, __file_handler
    try:
        current_date = datetime.now().strftime("%Y%m%d")
        if current_date != __current_date:
            if __file_handler:
                __LOGGER.removeHandler(__file_handler)
                __file_handler.close()
            __current_date = current_date
            __file_handler = FileHandler(f'logs/cte_search_{current_date}.log')
            __file_handler.setFormatter(formatter)
            __file_handler.setLevel('DEBUG')
            __LOGGER.addHandler(__file_handler)
    except Exception as e:
        __LOGGER.error(f"Failed to update log file handler: {e}")

async def logger_loop():
    """Initializes logger with both file and stream handlers.
    
    This function must be run before any logging functions can be used.
    It creates the initial log file handler and starts an infinite loop
    that checks for date changes every minute to rotate log files.
    """
    global __current_date, __file_handler, __ready

    # Set up file handler
    __current_date = datetime.now().strftime("%Y%m%d")
    __file_handler = FileHandler(f'logs/cte_search_{__current_date}.log')
    __file_handler.setFormatter(formatter)
    __file_handler.setLevel('DEBUG')
    __LOGGER.addHandler(__file_handler)
    __ready = True
    # Start async log file updater
    while True:
        await update_file_handler()
        await asyncio.sleep(60)  # Check every minute

def add_error_callback(callback: Callable[[str], None]):
    """Add a callback function to be called when errors occur.
    
    Args:
        callback: A function that takes a string parameter containing the error message
    """
    __error_callbacks.append(callback)

def info(msg):
    """Log an info level message.
    
    Args:
        msg: The message to log
    
    Raises:
        RuntimeError: If logger_loop() hasn't been started
    """
    if not __ready:
        raise RuntimeError("Ensure Logger Loop is running before you trying to use logging")
    __LOGGER.info(msg)

def debug(msg):
    """Log a debug level message.
    
    Args:
        msg: The message to log
    
    Raises:
        RuntimeError: If logger_loop() hasn't been started
    """
    if not __ready:
        raise RuntimeError("Ensure Logger Loop is running before you trying to use logging")
    __LOGGER.debug(msg)

def warning(msg):
    """Log a warning level message.
    
    Args:
        msg: The message to log
    
    Raises:
        RuntimeError: If logger_loop() hasn't been started
    """
    if not __ready:
        raise RuntimeError("Ensure Logger Loop is running before you trying to use logging")
    __LOGGER.warning(msg)

def error(msg):
    """Log an error level message.
    
    Args:
        msg: The message to log
    
    Raises:
        RuntimeError: If logger_loop() hasn't been started
    """
    if not __ready:
        raise RuntimeError("Ensure Logger Loop is running before you trying to use logging")
    __LOGGER.error(msg)
    for callback in __error_callbacks:
        try:
            callback(msg)
        except Exception as e:
            __LOGGER.error(f"Error callback failed: {e}")

def critical(msg):
    """Log a critical level message.
    
    Args:
        msg: The message to log
    
    Raises:
        RuntimeError: If logger_loop() hasn't been started
    """
    if not __ready:
        raise RuntimeError("Ensure Logger Loop is running before you trying to use logging")
    __LOGGER.critical(msg)
    for callback in __error_callbacks:
        try:
            callback(msg)
        except Exception as e:
            __LOGGER.error(f"Error callback failed: {e}")