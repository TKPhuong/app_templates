# system process as a thread
import queue
import threading
import traceback
from logging import Logger
from typing import Callable


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
        self._handlers[event].append(handler)

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
            for handler in self._handlers[event]:
                handler(instance, *args, **kwargs)
        except KeyError as e:
            e.args = (f"イベント {event} の処理が登録されていません。", )
            raise e


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
                raise Exception(f"Thread {self.name} はすでに開始されています。")
            self.thread = threading.Thread(target=self.run, name=self.name)
            self.thread.start()
        else:
            self.run()

    def stop(self):
        """Stop the thread"""
        self.should_stop = True
        self.task_queue.put(None)
        if self.thread is None:
            self.logger.error(Exception(f"Thread {self.name} not started"))
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
            self.thread_initiate()
            while not self.should_stop:
                try:
                    if self.event:
                        self.event.wait()
                        
                    task = self.task_queue.get(timeout=self.q_timeout)
                    if task is None:
                        break
                    # Handle the incoming command
                    self.logger.debug(f"Thread {self.name} received task={task}")
                    command = task.get("cmd")
                    self.cmd_dispatcher.dispatch(command, instance=self, task=task)
                    # Mark task as done
                    self.task_queue.task_done()
                except queue.Empty:
                    pass
        except Exception as e:
            self.logger.error(f"Thread {self.name} エラー： {e}")
            traceback_str = traceback.format_exc()
            self.logger.error(f"詳細なトレースバック：\n{traceback_str}")
            self._propagate_err_2_parent(e)
        finally:
            self.thread_cleanup()
            self.logger.info(f"{self.name} スレッドが停止しました。")

    def thread_initiate(self):
        """
        スレッドが開始されたときに、必要なセットアップ作業を行う。

        Returns
        -------
        None
        """
        self.command_register()
        self.logger.info(f"{self.name} スレッドが開始されました。")
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
        self.logger.info(f"Thread {self.name} received propagated error {e} from Thread {child_name}")
        #現在は子で捉えたエラーを再発生させるだけだが、具体的なエラー処理をここに書く(子スレッドの再起動、システムの終了…)
        raise e
        ...
    
    #書き直す対象
    def thread_cleanup(self):
        """
        main_loopの実行後に実行する必要があるクリーンアップ作業。

        Returns
        -------
        None
        """
        # クリーンアップの処理を書く
        ...

    def initiate_shutdown(self):
        """他のスレッドにシャットダウンを通知する。"""
        self.logger.info(f"Thread {self.name} が他のスレッドにシャットダウン・シグナルを送信しています...")
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
            self.logger.info(f"Thread {self.name} がエラー {e} を {self.parent.name} に伝播しました。")
        else:
            pass
