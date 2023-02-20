import os
import sys
import shutil
import logging

# add the parent directory of the current file to the system path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from templates.utils.log_tools.logger import Logger
FILE_PATH = os.path.join(current_dir, 'log/log.txt')

# Initialize the logging system with default settings
logger = Logger(file_path=FILE_PATH)
root_logger = logger.get_logger()

# Get a child logger with the name "myapp.module1" and a higher logging level
module1_logger = logger.get_logger('module1')

# Log a message using the main logger and the child logger
root_logger.info('This is a message from the main logger.')
module1_logger.error('This is an error message from the module1 logger.')