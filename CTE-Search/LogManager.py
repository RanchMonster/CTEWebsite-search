from logging import Logger, FileHandler, StreamHandler, Formatter
import os
from datetime import datetime
import asyncio

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
    """Initializes logger with both file and stream handlers."""
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

# Logging functions
def info(msg):
    if not __ready:
        raise RuntimeError("Ensure Logger Loop is running before you trying to use logging")
    __LOGGER.info(msg)

def debug(msg):
    if not __ready:
        raise RuntimeError("Ensure Logger Loop is running before you trying to use logging")
    __LOGGER.debug(msg)

def warning(msg):
    if not __ready:
        raise RuntimeError("Ensure Logger Loop is running before you trying to use logging")
    __LOGGER.warning(msg)

def error(msg):
    if not __ready:
        raise RuntimeError("Ensure Logger Loop is running before you trying to use logging")
    __LOGGER.error(msg)

def critical(msg):
    if not __ready:
        raise RuntimeError("Ensure Logger Loop is running before you trying to use logging")
    __LOGGER.critical(msg)
