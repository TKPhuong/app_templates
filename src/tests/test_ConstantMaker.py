import os
import sys
import pytest

# add the parent directory of the current file to the system path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from templates.system.constant import ConstantMaker

@pytest.fixture
def states():
    class States(metaclass=ConstantMaker):
        """
        システムの状態を表す定数を定義するクラスです。
        """
        idle = "IDLE"
        process = "PROCESSING"
        shutdown = "OFF"
    return States


@pytest.fixture
def error_codes():
    class ErrorCode(metaclass=ConstantMaker):
        """
        エラーコードを表す定数を定義するクラスです。
        """
        NOT_FOUND = "E001"
        PERMISSION_DENIED = "E002"
        INTERNAL_ERROR = "E003"
    return ErrorCode


@pytest.mark.parametrize("constant_name, constant_value", [
    ("idle", "IDLE"),
    ("process", "PROCESSING"),
    ("shutdown", "OFF")
])
def test_states_constants_access(states, constant_name, constant_value):
    """
    Statesクラスで定義された定数にアクセスできることを確認するテストです。
    """
    assert getattr(states, constant_name) == constant_value
    assert states[constant_name] == constant_value


@pytest.mark.parametrize("constant_name, constant_value", [
    ("NOT_FOUND", "E001"),
    ("PERMISSION_DENIED", "E002"),
    ("INTERNAL_ERROR", "E003")
])
def test_error_codes_constants_access(error_codes, constant_name, constant_value):
    """
    ErrorCodeクラスで定義された定数にアクセスできることを確認するテストです。
    """
    assert getattr(error_codes, constant_name) == constant_value
    assert error_codes[constant_name] == constant_value


@pytest.mark.parametrize("constant_name", [
    "nonexistent_constant",
    "nonexistent_constant",
])
def test_invalid_constant_access(states, error_codes, constant_name):
    """
    存在しない定数にアクセスすることができないことを確認するテストです。
    """
    with pytest.raises(AttributeError):
        getattr(states, constant_name)
    with pytest.raises(KeyError):
        states[constant_name]
    with pytest.raises(AttributeError):
        getattr(error_codes, constant_name)
    with pytest.raises(KeyError):
        error_codes[constant_name]


def test_constant_assignment(states, error_codes):
    """
    定数に新しい値を代入しようとするとTypeErrorが発生することを確認するテストです。
    """
    with pytest.raises(TypeError):
        states.idle = "NEW_IDLE_VALUE"
    with pytest.raises(TypeError):
        error_codes.NOT_FOUND = "NEW_E001_VALUE"


def test_constant_iteration(states, error_codes):
    """
    定数がイテラブルであることを確認するテストです。
    """
    assert set(states) == {"idle", "process", "shutdown"}
    assert set(error_codes) == {"NOT_FOUND", "PERMISSION_DENIED", "INTERNAL_ERROR"}


def test_constant_items(states, error_codes):
    """
    定数が辞書のような形式でアクセスできることを確認するテストです。
    """
    assert dict(states.items()) == {"idle": "IDLE", "process": "PROCESSING", "shutdown": "OFF"}
    assert dict(error_codes.items()) == {"NOT_FOUND": "E001", "PERMISSION_DENIED": "E002", "INTERNAL_ERROR": "E003"}

def test_constant_values(states, error_codes):
    """
    定数の値のリストを取得できることを確認するテストです。
    """
    assert list(states.values()) == ["IDLE", "PROCESSING", "OFF"]
    assert list(error_codes.values()) == ["E001", "E002", "E003"]