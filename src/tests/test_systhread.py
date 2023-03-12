import queue
import threading
from unittest.mock import MagicMock
import os
import sys
import pytest

# from pytest_mock import mocker

# @pytest.fixture()
# def mocker():
#     return mocker

# このファイルの親ディレクトリをシステムパスに追加する
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from templates.threadman.sys_thread import SysThread


class MockLogger:
    def __init__(self):
        self.logs = []

    def info(self, log):
        self.logs.append(log)

    def error(self, log):
        self.logs.append(log)

    def debug(self, log):
        self.logs.append(log)


@pytest.fixture
def sys_queues():
    test_q = queue.Queue()
    q1 = queue.Queue()
    q2 = queue.Queue()
    q3 = queue.Queue()
    return {"test": test_q, "q1": q1, "q2": q2, "q3": q3}


def test_sys_thread_start_stop(sys_queues):
    logger = MockLogger()
    thread = SysThread(name="test", logger=logger, sys_queues=sys_queues, is_main=False)
    assert thread.thread is None

    # start
    thread.start()
    assert isinstance(thread.thread, threading.Thread)

    # stop
    thread.stop()
    assert thread.thread is None


def test_sys_thread_add_task2queue(sys_queues):
    logger = MockLogger()
    thread = SysThread(name="test", logger=logger, sys_queues=sys_queues, is_main=False)
    task = {"key": "value"}
    queue_name = "q1"
    thread.add_task2queue(queue_name, task)
    assert sys_queues[queue_name].get() == task


def test_sys_thread_handle_example_command(sys_queues):
    logger = MockLogger()
    thread = SysThread(name="test", logger=logger, sys_queues=sys_queues, is_main=False)
    task = {"cmd": "CMD_EXAMPLE"}
    thread.handle_example_command(task=task)
    # assert some result


def test_sys_thread_handle_child_exception_command(sys_queues):
    logger = MockLogger()
    thread = SysThread(name="test", logger=logger, sys_queues=sys_queues, is_main=False)
    task = {"cmd": "CHILD_EXCEPTION", "name": "child", "exception": Exception("error")}
    with pytest.raises(Exception):
        thread.handle_child_exception_command(task=task)


def test_sys_thread_thread_cleanup(sys_queues):
    logger = MockLogger()
    thread = SysThread(name="test", logger=logger, sys_queues=sys_queues, is_main=False)
    thread.thread_cleanup()
    # assert some result


def test_sys_thread_initiate_shutdown(sys_queues):
    logger = MockLogger()
    thread = SysThread(name="test", logger=logger, sys_queues=sys_queues, is_main=False)
    thread.initiate_shutdown()
    assert sys_queues["q1"].get() is None
    assert sys_queues["q2"].get() is None
    assert sys_queues["q3"].get() is None


def test_sys_thread_propagate_err_2_parent(sys_queues):
    logger = MockLogger()
    parent = MagicMock()
    thread = SysThread(name="test", logger=logger, sys_queues=sys_queues, is_main=False, parent=parent)
    e = Exception("error")
    thread._propagate_err_2_parent(e)
    parent.task_queue.put.assert_called_with({"cmd": "CHILD_EXCEPTION", "exception": e, "from": "test"})
    assert logger.logs[-1] == f"Thread {thread.name} がエラー {e} を {parent.name} に伝播しました。"
