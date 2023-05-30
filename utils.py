import timeit
import logger

log = logger.setup_logger("logs/utils.log")
# log = logger.setup_logger(f'{__name__}.log')


def measure_time(func):
    def wrapper(*args, **kwargs):
        execution_time = timeit.timeit(lambda: func(*args, **kwargs), number=1)
        log.info(
            f"Function '{func.__name__}' took {execution_time:.6f} seconds to execute"
        )

    return wrapper


def raise_for_type(value, expected_type):
    if not isinstance(value, expected_type):
        raise TypeError(
            f"Value should be of type '{expected_type.__name__}'. Received value of type {type(value)}"
        )

def bytes_to_str(data: bytes) -> str:
    return data.decode().strip()

def str_to_bytes(data: str) -> bytes:
    return data.encode()

