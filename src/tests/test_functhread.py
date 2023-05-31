import time
import sys
import os

# このファイルの親ディレクトリをシステムパスに追加する
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from templates.threadman.func_thread import FuncThread

def test_one_time_thread():
    results = []

    def append_result():
        results.append('Hello, World!')

    thread = FuncThread(target=append_result, name="thread1")
    thread.start()

    time.sleep(1)
    thread.stop()

    assert results == ['Hello, World!']


def test_recurring_thread():
    results = []

    def append_result():
        results.append('Hello, World!')

    thread = FuncThread(target=append_result, name="thread1",interval=1)
    thread.start()

    time.sleep(3.5)
    thread.stop()

    assert len(results) == 4