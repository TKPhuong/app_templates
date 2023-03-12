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
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(handler)

    def dispatch(self, event: str, instance, *args, **kwargs):
        try:
            for handler in self._handlers[event]:
                handler(instance, *args, **kwargs)
        except KeyError as e:
            e.args = (f"There is no handler registered for event {event}", )
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

    #書き直す対象
    #SysThreadを継承するとき、各コマンドに定義した処理を登録する
    def command_register(self):
        self.cmd_dispatcher.register_handler("CMD_EXAMPLE", self.handle_example_command)
        self.cmd_dispatcher.register_handler("CHILD_EXCEPTION", self.handle_child_exception_command)
        #SysThreadを継承するとき、以下のようにthread_initiateの処理を書き直す
        #super().thread_initiate()
        #処理を書く
        ...

    def start(self):
        """Start the thread if self is not main app else just start run"""
        if not self.is_main:
            if self.thread is not None:
                raise Exception(f"Thread {self.name} already started")
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
        """Add a task to the queue"""
        self.sys_queues[queue_name].put(task)

    def run(self):
        """Main loop of the thread"""
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
            self.logger.error(f"Thread {self.name} error: {e}")
            traceback_str = traceback.format_exc()
            self.logger.error(f"Detailed traceback:\n{traceback_str}")
            self._propagate_err_2_parent(e)
        finally:
            self.thread_cleanup()
            self.logger.info(f"Thread {self.name} stopped")

    #書き直す対象
    def thread_initiate(self):
        """Perform any necessary setup work when the thread is started"""
        self.command_register()
        self.logger.info(f"{self.name} thread started")
        #SysThreadを継承するとき、以下のようにthread_initiateの処理を書き直す
        #super().thread_initiate()
        #処理を書く
        ...

    #SysThreadを継承するとき、適切な処理を以下の形でクラスに追加する
    def handle_example_command(self, *args, **kwargs):
        #「コマンド名」を受信したときの処理。kwargsに受信したタスクが格納される
        task = kwargs["task"]
        #処理を書く
        ...

    #書き直す対象
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
        Any cleanup work to be done after main_loop has finished executing.
        """
        #クリーンアップの処理を書く
        ...

    def initiate_shutdown(self):
        """
        Inform other threads to shut down gracefully.
        """
        self.logger.info(f"Thread {self.name} send shutdown signal to other threads...")
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
        if self.parent:
            self.parent.task_queue.put({"cmd": "CHILD_EXCEPTION", "exception": e, "from": self.name}) 
            self.logger.info(f"Thread {self.name} propagate error {e} back to {self.parent.name}...")
        else:
            pass
