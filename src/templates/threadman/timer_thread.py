# Timer
from time import time, sleep
from threading import Timer
import datetime
from typing import Optional



class TimerThread():
    """
    スレッドタイマークラス。
    ----
    :Parameters:
        :time: int型。タイマーの時間。
        :time: int型。タイマー開始時刻。
        :handle_function: タイマー満了時に実行する処理。
    :Returns:
        : なし
    """

    def __init__(self, interval, handle_function, *args, **kwargs):
        self.interval = interval
        self.handle_function = handle_function
        self.thread = None
        self.args = args
        self.kwargs = kwargs

    def start(self, start_time:Optional[time] = None):
        self.start_time = start_time or time()
        self.thread = Timer(self.interval, self.handle_function,
                            args=self.args, kwargs=self.kwargs)
        self.thread.start()

    def cancel(self):
        if self.thread:
            self.thread.cancel()
            self.thread = None
        self.start_time = 0

    # @staticmethod
    # def _time2datetime(now):
    #     """
    #     現在の日付と時刻を取得するための関数
    #     :Parameters:
    #         :now: float型。time.time()の戻り値
    #     :Returns:
    #         :now_ymdhms: 現在の年月日時分秒
    #     """
    #     # 現在の年、月、日、時、分、秒
    #     now_ymdhms = datetime.datetime.fromtimestamp(now)
    #     now_ymdhms = now_ymdhms.strftime("%Y年%m月%d日%H時%M分%S秒")
    #     return now_ymdhms


if __name__ == "__main__":
    def func(name):
        start_time = time()
        print(f"handle {name} passed to init executed, time:{start_time}")
    t = TimerThread(1, func, name="func1")
    now = time()
    t.cancel()
    # print(now)
    t.start()
    sleep(2)
    t.start()
    # sleep(5)