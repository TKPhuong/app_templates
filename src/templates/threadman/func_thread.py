# 関数をスレッドとして実行する
import threading
from typing import Optional, Union, List, Tuple, Callable

class FuncThread(threading.Thread):
    """
    関数をスレッドとして実行できるようにするためのカスタムスレッドクラス。
    ワンタイムスレッドとリカーリングスレッドのどちらかを指定することができます。
    """

    def __init__(self, target:Callable, name:str , args:Union[List, Tuple]=(),
                        kwargs:dict={}, interval:Optional[int]=None):
        """
        FuncThreadクラスの新しいインスタンスを初期化します。
        :param target: スレッドで実行する関数
        :param args: 関数に渡す引数
        :param kwargs: 関数に渡すキーワード引数
        :param interval: 関数を実行する間隔（秒単位）
        """
        super().__init__()
        self.target = target
        self.name = name
        self.args = args
        self.kwargs = kwargs or {}
        self.interval = interval
        self.event = threading.Event()

    def start(self):
        """
        スレッドを開始する。
        """
        self.event.clear()
        super().start()

    def run(self):
        """
        スレッドで関数を実行します。
        """
        while not self.event.is_set():
            self.target(*self.args, **self.kwargs)
            if not self.interval:
                # ワンタイムスレッドの場合は、最初の実行後にループを終了します
                break
            # リカーリングスレッドの場合は、指定された間隔を待ってから関数を再実行します
            self.event.wait(self.interval)

    def stop(self):
        """
        Stops the thread from running.
        """
        self.event.set()
        while self.is_alive():
            pass


if __name__ == "__main__":
    import time

    def print_hello(name):
        print(f'Hello, {name}!')

    # ワンタイムスレッドを作成する
    t1 = FuncThread(target=print_hello, name="OneTimeThread", args=('Alice',))
    t1.start()

    # スレッドの実行が完了するまで待機する
    t1.join()

    # ループするスレッドを作成する
    t2 = FuncThread(target=print_hello, name="RecurrentThread", args=('Bob',), interval=1)
    t2.start()

    # 5秒待機する
    time.sleep(5)
    print(f"{t2.is_alive()=}")
    # スレッドの実行を停止する
    t2.stop()
    print(f"{t2.is_alive()=}")