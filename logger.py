# logger.py
import logging
import os

LOG_FILE = os.path.join(os.path.dirname(__file__), 'lute_importer.log')

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_info(message):
    logging.info(message)

def log_error(message):
    logging.error(message)