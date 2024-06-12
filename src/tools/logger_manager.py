import logging
import os
import sys
import inspect

LOGS_DIR = 'log/'

def setup_logging():
    log_filename = inspect.stack()[1].filename.replace(".py", "").split('/')[-1]
    file_handler = logging.FileHandler(filename=f'{LOGS_DIR}{log_filename}.log')
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', handlers=[file_handler, stdout_handler] , level=logging.INFO)
    logging.info('\n')
    logging.info('Starting script execution')

if __name__ == '__main__':
    setup_logging()
    logging.info('test')