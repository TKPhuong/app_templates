import logging
import re
import os
import shutil
import sys

# add the parent directory of the current file to the system path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from templates.utils.log_tools.logger import Logger


def test_logger():
    logger = Logger(level="debug")
    my_logger = logger.get_logger("my_module")

    my_logger.debug("debug message")
    my_logger.info("info message")
    my_logger.warning("warning message")
    my_logger.error("error message")
    my_logger.critical("critical message")

    # Check that log file was created
    assert os.path.exists("./log/log.txt")

    # Check that log file contains the expected messages
    with open("./log/log.txt", "r") as log_file:
        log_contents = log_file.read()
        assert "debug message" in log_contents
        assert "info message" in log_contents
        assert "warning message" in log_contents
        assert "error message" in log_contents
        assert "critical message" in log_contents

        # Check that log messages are formatted correctly
        expected_log_message = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} DEBUG test_logger.py my_module: debug message\n"
        assert re.search(expected_log_message, log_contents) is not None

    # Shut down logging system to remove the temporary log directory
    logging.shutdown()

    # Clean up log file and directory
    shutil.rmtree("./log")
