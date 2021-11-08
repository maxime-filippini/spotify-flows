import logging
from logging import StreamHandler
from logging.handlers import RotatingFileHandler


def init_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    logger_handler = RotatingFileHandler("logs/log.log")
    logger_handler.setLevel(logging.INFO)

    console_handler = StreamHandler()
    console_handler.setLevel(logging.INFO)

    logger_formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

    logger_handler.setFormatter(logger_formatter)
    console_handler.setFormatter(logger_formatter)

    logger.addHandler(logger_handler)
    logger.addHandler(console_handler)

    return logger
