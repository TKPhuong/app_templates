# system process as a thread
import queue
import threading
import traceback
from logging import Logger
from typing import Callable
from enum import Enum
import functools


class States(Enum):
    STARTUP = "スタートアップ"
    INITIATING = "初期化中"
    IDLE = "タスク待ち"
    PROCESSING = "タスク処理中"
    CLEANUP = "クリーンアップ"
    EXITED = "終了"


class CmdDispatcher:
    def __init__(self):
        self._handlers = {}

    def register_handler(self, event: str, handler: Callable):
        """
        イベントに対する処理を登録する。

        Parameters
        ----------
        event : str
            イベント名。
        handler : Callable
            イベントハンドラ。

        Returns
        -------
        None
        """
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(self._log_handler(handler))

    def dispatch(self, event: str, instance, *args, **kwargs):
        """
        イベントを発火させ、登録された処理を実行する。

        Parameters
        ----------
        event : str
            発火するイベント名。
        instance : any
            処理を実行するオブジェクト。
        *args : any
            処理に渡す引数。
        **kwargs : any
            処理に渡すキーワード引数。

        Returns
        -------
        None
        """
        try:
            instance._state = States.PROCESSING
            for handler in self._handlers[event]:
                handler(instance, *args, **kwargs)
        except KeyError as key_err:
            raise KeyError(f"イベント {event} の処理が登録されていません。", )
        except ValueError as val_err:
            raise val_err
        except Exception as err:
            raise err
    
    def _log_handler(self, fn):
        """自動でタスクのログを出力するデコレーター。"""
        @functools.wraps(fn)
        def wrapped(self, *args, **kwargs):
            task = kwargs["task"]
            # Make sure task has required keys
            if not all(key in task for key in ["cmd", "from"]):
                raise ValueError(f"不正なタスク形式が受信しました。'cmd' と 'from' のキーが必要です: タスク＝{task}。", )
            self.logger.info(f"スレッド {self.name} が スレッド {task['from']} から CMD={task['cmd']} を受け取りました")
            result = fn(self, *args, **kwargs)
            self.logger.info(f"スレッド {self.name} が CMD={task['cmd']} を処理しました")
            return result
        return wrapped
        

class SysThread:
    def __init__(self, name:str, logger:Logger, sys_queues:queue.Queue,
                   is_main=False, q_timeout=5, *args, **kwargs):
        self.name = name
        self.logger = logger
        self.task_queue = sys_queues[self.name]
        self.sys_queues = sys_queues
        self.thread = None
        self.should_stop = False
        self.args = args
        self.is_main = is_main
        self.q_timeout = q_timeout
        self.parent = kwargs.get("parent", None)
        self.event = kwargs.get("event", None)
        self.cmd_dispatcher = CmdDispatcher()
        self._state = States.STARTUP
        self._error = None
        self._thread_prefix = "Thread" if not is_main else "MainThread"
    
    @property
    def state(self):
        return self._state

    @property
    def error(self):
        return self._error

    def command_register(self):
        """
        SysThreadを継承するクラスで、コマンド名に応じた処理を登録するメソッド。
        """
        self.cmd_dispatcher.register_handler("CMD_EXAMPLE", self.handle_example_command)
        self.cmd_dispatcher.register_handler("CHILD_EXCEPTION", self.handle_child_exception_command)
        # SysThreadを継承するとき、以下のようにthread_initiateの処理を書き直す
        # super().thread_initiate()
        # 処理を書く
        ...

    def start(self):
        """スレッドを起動する。"""
        if not self.is_main:
            if self.thread is not None:
                raise Exception(f"{self._thread_prefix} {self.name} はすでに開始されています。")
            self.thread = threading.Thread(target=self.run, name=self.name)
            self.thread.start()
        else:
            self.run()

    def stop(self):
        """Stop the thread"""
        self.should_stop = True
        self.task_queue.put(None)
        if self.thread is None:
            self.logger.error(Exception(f"{self._thread_prefix} {self.name} not started"))
        else:
            self.thread.join()
        self.thread = None

    def join(self):
        while self.thread is not None:
            pass

    def add_task2queue(self, queue_name, task):
        """
        タスクをキューに追加する。

        Parameters
        ----------
        queue_name : str
            キュー名。
        task : any
            追加するタスク。

        Returns
        -------
        None
        """
        self.sys_queues[queue_name].put(task)

    def run(self):
        """スレッドのメインループ。"""
        try:
            self.logger.info(f"{self._thread_prefix} {self.name} が開始されました。")
            self.thread_initiate()
            self.logger.info(f"{self._thread_prefix} {self.name} の初期化が完了しました。")
            self._state = States.IDLE
            while not self.should_stop:
                try:
                    if self.event:
                        self.event.wait()
                    
                    task = self.task_queue.get(timeout=self.q_timeout)
                    if task is None:
                        break
                    # Handle the incoming command
                    self.logger.debug(f"{self._thread_prefix} {self.name} received task={task}")
                    command = task.get("cmd")
                    self.cmd_dispatcher.dispatch(command, instance=self, task=task)
                    self._state = States.IDLE
                    # Mark task as done
                    self.task_queue.task_done()
                except queue.Empty:
                    pass
        except Exception as e:
            self.logger.exception(
                f"{self._thread_prefix} {self.name} が「{self._state.value}」の状態でエラー発生： {e}"
            )
            self._error = e
            self._propagate_err_2_parent(e)
        finally:
            try:
                self.thread_cleanup()
                self.logger.info(f"{self._thread_prefix} {self.name} のクリーンアップが完了しました。")
                self._state = States.EXITED
            except Exception as e:
                self.logger.exception(
                    f"{self._thread_prefix} エラーのクリーンアップを実施している際に、異なるエラーが発生しました： {e}"
                )
                self.logger.warning(f"{self._thread_prefix} {self.name} がクリーンアップ処理を実施できず、停止します...")
            finally:
                self.logger.info(f"{self._thread_prefix} {self.name} が停止しました。")

    def thread_initiate(self):
        """
        スレッドが開始されたときに、必要なセットアップ作業を行う。

        Returns
        -------
        None
        """
        self._state = States.INITIATING
        self.command_register()
        self.logger.info(f"{self._thread_prefix} {self.name} が初期化を開始します…")
        # SysThreadを継承するとき、以下のようにthread_initiateの処理を書き直す
        # super().thread_initiate()
        # 処理を書く
        ...

    #SysThreadを継承するとき、適切な処理を以下の形でクラスに追加する
    def handle_example_command(self, *args, **kwargs):
        """
        コマンド名 "CMD_EXAMPLE" を受信したときの処理。

        Parameters
        ----------
        *args : any
            引数。
        **kwargs : any
            キーワード引数。

        Returns
        -------
        None
        """
        #「コマンド名」を受信したときの処理。kwargsに受信したタスクが格納される
        task = kwargs["task"]
        #処理を書く
        ...

    #書き直す対象, handle_command の１つの例
    def handle_child_exception_command(self, *args, **kwargs):
        #「CHILD_EXCEPTION」を受信したときの処理
        #SysThreadを継承するとき、以下のようにhandle_child_exception_commandの処理を書き直す
        task = kwargs["task"]
        child_name = task.get("name")
        e = task.get("exception")
        self.logger.info(f"{self._thread_prefix} {self.name} received propagated error {e} from Thread {child_name}")
        #現在は子で捉えたエラーを再発生させるだけだが、具体的なエラー処理をここに書く(子スレッドの再起動、システムの終了…)
        raise e
        ...

    #SysThreadを継承するとき、適切な処理を以下の形でクラスに追加する
    def handle_custom_command(self, *args, **kwargs):
        #「"CUSTOM_COMMAND"」を受信したときの処理。kwargsに受信したタスクが格納される
        task = kwargs["task"]
        #処理を書く

    #書き直す対象
    def thread_cleanup(self):
        """
        main_loopの実行後に実行する必要があるクリーンアップ作業。

        Returns
        -------
        None
        """
        self.logger.info(f"{self._thread_prefix} {self.name} がクリーンアップを開始します…")
        self._state = States.CLEANUP
        # SysThreadを継承するとき、以下のようにthread_cleanup()の処理を書き直す
        # super().thread_cleanup()
        # クリーンアップの処理を書く
        ...

    def initiate_shutdown(self):
        """他のスレッドにシャットダウンを通知する。"""
        self.logger.info(f"{self._thread_prefix} {self.name} が他のスレッドにシャットダウン・シグナルを送信しています...")
        for name, queue in self.sys_queues.items():
            if name != self.name:
                queue.put(None)

    def __eq__(self, other):
        if not isinstance(other, SysThread):
            return False
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def _propagate_err_2_parent(self, e):
        """
        親スレッドにエラーを伝播する。

        Parameters
        ----------
        e : Exception
            伝播する例外。

        Returns
        -------
        None
        """
        if self.parent:
            self.parent.task_queue.put({"cmd": "CHILD_EXCEPTION", "exception": e, "from": self.name}) 
            self.logger.info(f"{self._thread_prefix} {self.name} がエラー {e} を {self.parent.name} に伝播しました。")
        else:
            pass

if __name__ == "__main__":

    class MyThread(SysThread):

        def thread_initiate(self):
            super().thread_initiate()
            # ここで必要な初期化処理を実行する

        def command_register(self):
            super().command_register()
            self.cmd_dispatcher.register_handler("CUSTOM_COMMAND", self.handle_custom_command)

        #SysThreadを継承するとき、適切な処理を以下の形でクラスに追加する
        def handle_custom_command(self, *args, **kwargs):
            #「"CUSTOM_COMMAND"」を受信したときの処理。kwargsに受信したタスクが格納される
            task = kwargs["task"]
            #処理を書く
            ...

        def thread_cleanup(self):
            super().thread_cleanup()
            # ここで必要なクリーンアップ処理を実行する
