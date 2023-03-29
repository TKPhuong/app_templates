from time import time, sleep
import sys
import os

# このファイルの親ディレクトリをシステムパスに追加する
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from templates.threadman.timer_thread import TimerThread

class TestTimerThread:
    def test_init(self):
        timer = TimerThread(10, lambda: None)
        assert timer.interval == 10
        assert timer.handle_function.__name__ == '<lambda>'
        assert timer.thread is None
        assert timer.args == ()
        assert timer.kwargs == {}

    def test_start(self):
        def handle_function():
            pass

        timer = TimerThread(2, handle_function)
        timer.start()
        assert timer.thread.is_alive()

        start_time = time()
        timer.start(start_time)
        assert timer.start_time == start_time
    
    def test_handle_function_execution(self):
        test_list = [1, 2, 3]
        def handle_function(test_list=test_list):
            test_list.append(4)

        timer = TimerThread(2, handle_function)
        timer.start()
        sleep(2.5)
        assert test_list == [1, 2, 3, 4]

    def test_cancel(self):
        timer = TimerThread(10, lambda: None)
        timer.start()
        timer.cancel()
        assert not timer.thread
        assert timer.start_time == 0