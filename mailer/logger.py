import logging
from flask import Flask

def setup_logger(app: Flask):
    logger = app.logger
    logger.setLevel(logging.INFO)

    # Remove existing handlers
    for handler in logger.handlers:
        logger.removeHandler(handler)

    file_handler = logging.FileHandler('app.log')
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
