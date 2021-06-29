import time
import logging

logger = logging.getLogger()

def now_ms():
    return time.time() * 1E3


def now_ns():
    return time.time_ns()


def hour_to_nano(hours):
    return hours*36E11


def min_to_nano(mins):
    return mins*6E10


def profile_func(name):
    def inner(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed = round((time.time() - start_time) * 1E3, 4)
            logger.info(f'profile "{name}": elapsed {elapsed} ms')
            return result
        return wrapper
    return inner