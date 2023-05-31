import logging
import re
import os
import sys
import pytest

# add the parent directory of the current file to the system path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from templates.utils.log_tools.logger import Logger


@pytest.fixture
def logger(tmpdir):
    log_file = tmpdir.join("log.txt")
    logger = Logger(file_path=str(log_file))
    yield logger
    logging.shutdown()


def test_logger_output(logger, tmpdir):

    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

    with open(logger.handlers[1].baseFilename, "r") as f:
        log_contents = f.read()
        assert "This is a debug message" not in log_contents
        assert "This is an info message" in log_contents
        assert "This is a warning message" in log_contents
        assert "This is an error message" in log_contents
        assert "This is a critical message" in log_contents
        
        # check that messages are in the correct format
        log_lines = log_contents.strip().split('\n')
        datestamp_pattern = r'\d{4}-\d{2}-\d{2}'
        timestamp_pattern = r'\d{2}:\d{2}:\d{2},\d{3}'
        for line in log_lines:
            format, message = line.strip().split(": ")
            parts = format.strip().split(" ")
            assert len(parts) == 5
            assert re.match(datestamp_pattern, parts[0])
            assert re.match(timestamp_pattern, parts[1])
            assert parts[2] in ['[DEBUG]', '[INFO]', '[WARNING]', '[ERROR]', '[CRITICAL]']
            assert re.match(r'.*\.py:\d+$', parts[3]) is not None # filename:line_number
            assert parts[4].startswith('main')
            assert message.startswith('This is ')
            


def test_logger_child(logger):
    child_logger = logger.getChild("child")
    assert child_logger.name == "main.child"
    assert child_logger.level == logging.INFO


