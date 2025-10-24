import time
from functools import wraps
from .logger import logger

def measure_duration(func):
    """
    Decorator to log the duration of a function call.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logger.info(f"{func.__name__} executed in {duration:.4f} seconds")
        return result
    return wrapper
