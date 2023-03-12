import os
import sys
import pytest

# このファイルの親ディレクトリをシステムパスに追加する
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from templates.system.status.sys_status import StatusTracker


# StatusTrackerインスタンスを生成するためのフィクスチャ
@pytest.fixture
def tracker():
    # 初期ステータスを指定してStatusTrackerインスタンスを生成
    initial_statuses = {
        "STATUS": "IDLE",
        "STORAGE_CHECK": "OK",
        "DISK_SPACE": 0.0,
        "CPU_USAGE": 0.0,
        "MEMORY_USAGE": 0.0,
        "DATABASE_CONNECTIONS": "OK",
        "LOG_FILE_SIZE": 0.0,
    }
    tracker = StatusTracker("system1", initial_statuses)
    yield tracker
    # テストが終了した後にStatusTrackerインスタンスを削除する
    StatusTracker.delete_instance("system1")


# StatusTrackerクラスのget_statusメソッドをテストする関数
def test_get_status(tracker):
    # 各ステータスを取得して正しい値が返ってくることを確認
    assert tracker.get_status("STATUS") == "IDLE"
    assert tracker.get_status("STORAGE_CHECK") == "OK"
    assert tracker.get_status("DISK_SPACE") == 0.0
    assert tracker.get_status("CPU_USAGE") == 0.0
    assert tracker.get_status("MEMORY_USAGE") == 0.0
    assert tracker.get_status("DATABASE_CONNECTIONS") == "OK"
    assert tracker.get_status("LOG_FILE_SIZE") == 0.0
    # 定義されていないステータスを取得しようとした場合にKeyErrorが発生することを確認
    with pytest.raises(KeyError):
        tracker.get_status("UNDEFINED_STATUS")


# StatusTrackerクラスの__setitem__とupdate_statusメソッドをテストする関数
def test_set_status(tracker):
    # ステータスを更新して正しい値が返ってくることを確認
    tracker["STATUS"] = "RUNNING"
    assert tracker["STATUS"] == "RUNNING"
    tracker.update_status("CPU_USAGE", 0.8)
    assert tracker.get_status("CPU_USAGE") == 0.8
    # 定義されていないステータスを更新しようとした場合にAttributeErrorが発生することを確認
    with pytest.raises(AttributeError):
        tracker["UNDEFINED_STATUS"] = "ERROR"


# StatusTrackerクラスのresetメソッドをテストする関数
def test_reset(tracker):
    # ステータスを更新してresetメソッドで初期化した際に正しい値が返ってくることを確認
    tracker["STATUS"] = "RUNNING"
    tracker.update_status("CPU_USAGE", 0.8)
    tracker.reset()
    assert tracker.get_status("STATUS") == "IDLE"
    assert tracker.get_status("CPU_USAGE") == 0.0

# StatusTrackerクラスの__iter__メソッドをテストする関数
def test_status_tracker_iter(tracker):
    # 各ステータスのキーと値を順番に取得して正しい値が返ってくることを確認
    expected_statuses = {
        "STATUS": "IDLE",
        "STORAGE_CHECK": "OK",
        "DISK_SPACE": 0.0,
        "CPU_USAGE": 0.0,
        "MEMORY_USAGE": 0.0,
        "DATABASE_CONNECTIONS": "OK",
        "LOG_FILE_SIZE": 0.0,
    }
    for status_name, status_val in tracker:
        assert status_name in expected_statuses
        assert status_val == expected_statuses[status_name]
        expected_statuses.pop(status_name)
    assert not expected_statuses  # 全てのステータスが取得されたことを確認

# StatusTrackerインスタンスのstring表現をテストする関数
def test_status_tracker_repr(tracker):
    # ステータスを設定する
    tracker["STATUS"] = "RUNNING"
    tracker.update_status("CPU_USAGE", 0.8)

    # 正しい文字列が出力されることを確認する
    assert repr(tracker) == "StatusTracker[system1](STATUS: 'RUNNING', STORAGE_CHECK: 'OK', DISK_SPACE: 0.0, CPU_USAGE: 0.8, MEMORY_USAGE: 0.0, DATABASE_CONNECTIONS: 'OK', LOG_FILE_SIZE: 0.0)"


# StatusTrackerクラスのdelete_instanceメソッドをテストする関数
def test_delete_instance():
    # 初期ステータスを指定して2つのStatusTrackerインスタンスを生成
    initial_statuses1 = {
        "STATUS": "IDLE",
        "STORAGE_CHECK": "OK",
        "DISK_SPACE": 0.0,
        "CPU_USAGE": 0.0,
        "MEMORY_USAGE": 0.0,
        "DATABASE_CONNECTIONS": "OK",
        "LOG_FILE_SIZE": 0.0,
    }
    initial_statuses2 = {
        "STATUS": "RUNNING",
        "STORAGE_CHECK": "OK",
        "DISK_SPACE": 100.0,
        "CPU_USAGE": 0.5,
        "MEMORY_USAGE": 0.3,
        "DATABASE_CONNECTIONS": "ERROR",
        "LOG_FILE_SIZE": 100.0,
    }
    tracker1 = StatusTracker("system1", initial_statuses1)
    tracker2 = StatusTracker("system2", initial_statuses2)
    # インスタンスを削除して存在しなくなったことを確認
    StatusTracker.delete_instance("system1")
    assert StatusTracker.get_instance("system1") is None
    # 別のインスタンスは削除されていないことを確認
    assert StatusTracker.get_instance("system2") is not None


# StatusTrackerクラスのSingletonパターンをテストする関数
def test_singleton():
    # 同じIDで2つのStatusTrackerインスタンスを生成して、同一のオブジェクトであることを確認
    initial_statuses = {
        "STATUS": "IDLE",
        "STORAGE_CHECK": "OK",
        "DISK_SPACE": 0.0,
        "CPU_USAGE": 0.0,
        "MEMORY_USAGE": 0.0,
        "DATABASE_CONNECTIONS": "OK",
        "LOG_FILE_SIZE": 0.0,
    }
    tracker1 = StatusTracker("system1", initial_statuses)
    tracker2 = StatusTracker("system1", initial_statuses)
    assert tracker1 is tracker2


# StatusTrackerクラスのインスタンスが独立していることをテストする関数
def test_multiple_instances():
    # 初期ステータスを指定して2つのStatusTrackerインスタンスを生成
    initial_statuses1 = {
        "STATUS": "IDLE",
        "STORAGE_CHECK": "OK",
        "DISK_SPACE": 0.0,
        "CPU_USAGE": 0.0,
        "MEMORY_USAGE": 0.0,
        "DATABASE_CONNECTIONS": "OK",
        "LOG_FILE_SIZE": 0.0,
    }
    initial_statuses2 = {
        "STATUS": "RUNNING",
        "STORAGE_CHECK": "OK",
        "DISK_SPACE": 100.0,
        "CPU_USAGE": 0.5,
        "MEMORY_USAGE": 0.3,
        "DATABASE_CONNECTIONS": "ERROR",
        "LOG_FILE_SIZE": 100.0,
    }
    tracker1 = StatusTracker("system1", initial_statuses1)
    tracker2 = StatusTracker("system2", initial_statuses2)
    tracker1["STATUS"] = "RUNNING"
    tracker2["MEMORY_USAGE"] = 0.6
    assert tracker1.get_status("STATUS") == "RUNNING"
    assert tracker1.get_status("MEMORY_USAGE") == 0.0
    assert tracker2.get_status("STATUS") == "RUNNING"
    assert tracker2.get_status("MEMORY_USAGE") == 0.6
    tracker1.reset()
    tracker2.reset()
    assert tracker1.get_status("STATUS") == "IDLE"
    assert tracker1.get_status("MEMORY_USAGE") == 0.0
    assert tracker2.get_status("STATUS") == "RUNNING"
    assert tracker2.get_status("MEMORY_USAGE") == 0.3


def test_status_tracker_initial_status_copy():
    initial_statuses = {
        "STATUS": "IDLE",
        "STORAGE_CHECK": "OK",
        "DISK_SPACE": 0.0,
        "CPU_USAGE": 0.0,
        "MEMORY_USAGE": 0.0,
        "DATABASE_CONNECTIONS": "OK",
        "LOG_FILE_SIZE": 0.0,
    }

    tracker = StatusTracker("system", initial_statuses)

    # tracker 生成後に initial_statuses を変更する
    initial_statuses["STATUS"] = "RUNNING"

    # tracker 内部に格納されている initial_status が、変更された initial_statuses と異なることを確認する
    assert tracker._initial_status["STATUS"] == "IDLE"
