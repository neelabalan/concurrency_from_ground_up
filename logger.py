import logging


def setup_logger(log_file, level=logging.INFO):
    # Create a logger if it doesn't exist already
    logger = logging.getLogger()
    if len(logger.handlers) > 0:
        # Handlers already exist, return the existing logger
        return logger

    logger.setLevel(level)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
