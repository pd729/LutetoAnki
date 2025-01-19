# logger.py
import logging
import os

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lute_importer.log')


# Configure the logger
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True  # Force reconfiguration (Python 3.8+)
)


def log_debug(message):
    logging.debug(message)


def log_info(message):
    logging.info(message)


def log_warning(message):
    logging.warning(message)


def log_error(message):
    logging.error(message)


def log_critical(message):
    logging.critical(message)
