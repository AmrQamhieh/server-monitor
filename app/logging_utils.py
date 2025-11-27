import logging
import os
from functools import wraps

# Log file name (you can change it if you want)
LOG_FILE = os.getenv("LOG_FILE", "server_monitor.log")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def setup_logging():
    """Configure root logging once for the whole app."""
    if getattr(setup_logging, "_configured", False):
        return  # avoid configuring multiple times

    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(LOG_FILE),
        ],
    )
    setup_logging._configured = True


def get_logger(name: str) -> logging.Logger:
    """Simple helper to get a logger with our config."""
    setup_logging()
    return logging.getLogger(name)


def log_action(func):
    """
    Decorator (wrapper function) to log when a function is called,
    when it finishes, and if it raises an error.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.info(f"Calling {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.exception(f"{func.__name__} failed with error: {e}")
            raise

    return wrapper
