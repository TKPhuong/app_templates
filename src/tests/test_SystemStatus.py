import os
import sys
import pytest

# このファイルの親ディレクトリをシステムパスに追加する
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from templates.system.status.sys_status import SystemStatus


@pytest.fixture
def system_status():
    status = SystemStatus()
    yield status
    status.reset()


def test_update_status(system_status):
    # Test that SystemStatus can update a status
    system_status.update_status("STORAGE_CHECK", "NG")
    assert system_status.get_status("STORAGE_CHECK") == "NG"


def test_get_status(system_status):
    # Test that SystemStatus can get a status
    assert system_status.get_status("STORAGE_CHECK") == "OK"


def test_get_missing_status(system_status):
    # Test that SystemStatus returns None for missing statuses
    assert system_status.get_status("NONEXISTENT_STATUS") is None


def test_setitem(system_status):
    # Test that SystemStatus can set a status like a dictionary
    system_status["DISK_SPACE"] = 20.0
    assert system_status["DISK_SPACE"] == 20.0


def test_getitem(system_status):
    # Test that SystemStatus can get a status like a dictionary
    assert system_status["DISK_SPACE"] == 0.0


def test_singleton(system_status):
    # Test that SystemStatus is a singleton
    status1 = system_status
    status1.update_status("STORAGE_CHECK", "NG")
    status2 = SystemStatus()
    assert status2.get_status("STORAGE_CHECK") == "NG"
    assert status1 == status2


def test_default_statuses(system_status):
    # Test that SystemStatus is initialized with default statuses
    assert system_status["STORAGE_CHECK"] == "OK"
    assert system_status["DISK_SPACE"] == 0.0
    assert system_status["CPU_USAGE"] == 0.0
    assert system_status["MEMORY_USAGE"] == 0.0
    assert system_status["DATABASE_CONNECTIONS"] == "OK"
    assert system_status["LOG_FILE_SIZE"] == 0.0


def test_initial_statuses(system_status):
    # Test that SystemStatus is initialized with specified statuses
    initial_statuses = {
        "STORAGE_CHECK": "NG",
        "DISK_SPACE": 30.0,
        "CPU_USAGE": 60.0,
        "MEMORY_USAGE": 50.0,
        "DATABASE_CONNECTIONS": "OK",
        "LOG_FILE_SIZE": 1.5,
    }
    system_status.reset()
    status = SystemStatus(initial_statuses)
    assert status["STORAGE_CHECK"] == "NG"
    assert status["DISK_SPACE"] == 30.0
    assert status["CPU_USAGE"] == 60.0
    assert status["MEMORY_USAGE"] == 50.0
    assert status["DATABASE_CONNECTIONS"] == "OK"
    assert status["LOG_FILE_SIZE"] == 1.5


def test_instance(system_status):
    # Test that only one instance of SystemStatus is created
    status1 = system_status
    status1.update_status("STORAGE_CHECK", "NG")
    status2 = SystemStatus()
    assert status1 == status2
    assert system_status.get_status("STORAGE_CHECK") == "NG"
