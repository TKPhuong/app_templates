import time
import datetime
import sys
import os
import re
import pytest

# このファイルの親ディレクトリをシステムパスに追加する
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from templates.utils.helper_funcs.display_time import timestamp2str


formats = [
    ("jap", "%Y年%m月%d日%H時%M分%S秒"),
    ("iso", None),
    ("us", "%m/%d/%Y %I:%M:%S %p"),
    ("uk", "%d/%m/%Y %H:%M:%S"),
]

@pytest.mark.parametrize("fmt,expected_format", formats)
def test_timestamp2str_float(fmt, expected_format):
    now = time.time()
    now_datetime = datetime.datetime.fromtimestamp(now)

    if fmt == "iso":
        expected_str = now_datetime.isoformat()
    else:
        expected_str = now_datetime.strftime(expected_format)

    formatted_str = timestamp2str(now, format=fmt)
    assert formatted_str == expected_str

@pytest.mark.parametrize("fmt,expected_format", formats)
def test_timestamp2str_datetime(fmt, expected_format):
    now_datetime = datetime.datetime.now()

    if fmt == "iso":
        expected_str = now_datetime.isoformat()
    else:
        expected_str = now_datetime.strftime(expected_format)

    formatted_str = timestamp2str(now_datetime, format=fmt)
    assert formatted_str == expected_str


def test_timestamp2str_invalid_input():
    invalid_input = "invalid_input"
    error_message = "無効な入力です。'now'はdatetime.datetimeオブジェクトかtime.time()の出力でなければなりません。"
    with pytest.raises(ValueError, match=re.escape(error_message)):
        timestamp2str(invalid_input)

def test_timestamp2str_invalid_format():
    now = time.time()
    invalid_format = "unsupported_format"
    error_message = "無効なフォーマットです。対応しているフォーマット: 'jap', 'iso', 'us', 'uk'。"
    with pytest.raises(ValueError, match=error_message):
        timestamp2str(now, format=invalid_format)
