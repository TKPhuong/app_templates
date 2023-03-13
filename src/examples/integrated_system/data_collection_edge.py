import time
from datetime import datetime
import sys
import os
import queue
import random
import threading
import json

# add the parent directory of the current file to the system path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir =  os.path.dirname(os.path.dirname(current_dir))
sys.path.append(parent_dir)

from templates.threadman.func_thread import FuncThread
from templates.threadman.sys_thread import SysThread
from templates.utils.helper_funcs.display_time import timestamp2str
from templates.utils.helper_funcs import check_file
from templates.utils.log_tools.logger import Logger

from sensor_thread  import SensorThread
from process_thread  import DataProcessThread
from db_thread  import EdgeDBThread
from sync_thread  import EdgeSynchronizeThread


class EdgeApp(SysThread):
    def __init__(self,
                name="edge1",
                log_level="debug",
                log_path = "./log.txt",
                comm_info={
                            "main":{"ip":"localhost", "port":5000},
                            "own":{"ip":"localhost", "port":5001}
                }
    ):  
        # Save communication info to instance
        self.comm_info = comm_info

        # Initialize logger
        logger = Logger(name="EdgeApp", level=log_level, file_path=log_path, backup_count=7)

        self.procs_name = {"main": name, "sensor": "sensor", 
                            "process":"data_process", "sync":"sync", "db":"database"}
        
        # Create queues
        queues = {v: queue.Queue() for k,v in self.procs_name.items()}

        # Create event handlers
        self.thread_handlers = {k: threading.Event() for k,v in self.procs_name.items() if k != "main"}

        self.threads = {}
        # Create threads
        self.threads["sensor"] = SensorThread(
            self.procs_name["sensor"], 
            logger.getChild(self.procs_name["sensor"]), 
            queues,
            parent=self,
            event=self.thread_handlers["sensor"],
        )
        self.threads["process"] = DataProcessThread(
            self.procs_name["process"],
            logger.getChild(self.procs_name["process"]),  
            queues,
            parent=self,
            event=self.thread_handlers["process"],
        )
        self.threads["sync"] = EdgeSynchronizeThread(
            self.procs_name["sync"], 
            logger.getChild(self.procs_name["sync"]), 
            queues,
            parent=self,
            event=self.thread_handlers["sync"],
            comm_info=self.comm_info,
        )
        self.threads["db"] = EdgeDBThread(
            self.procs_name["db"], 
            logger.getChild(self.procs_name["db"]), 
            queues,
            parent=self,
            event=self.thread_handlers["db"],
        )

        super().__init__(
            self.procs_name["main"], 
            logger, 
            queues,
            is_main=True,
            q_timeout=1
        )

    def command_register(self):
        super().command_register()
        self.cmd_dispatcher.register_handler("start_sensor", self.handle_start_sensor_command)

    def pause_thread(self, thread_name):
        self.thread_handlers[thread_name].clear()
        self.logger.info(f"Thread {self.name} paused")

    def resume_thread(self, thread_name):
        self.thread_handlers[thread_name].set()
        self.logger.info(f"{thread_name} thread resumed")

    def thread_initiate(self):
        super().thread_initiate()
        check_file("common.py", current_dir ,"001")

        # Start and Resume all the threads
        for thread_name in self.procs_name:
            if thread_name not in ["main"]:
                self.threads[thread_name].start()
                self.resume_thread(thread_name)
        
        # initiate sensor reading
        self.add_task2queue(self.name, {"cmd":"start_sensor", "from": self.name})

    def handle_start_sensor_command(self, *args, **kargs):
        self.start_sensor_thread = FuncThread(target=self._start_sensor_func, 
                                              name="start_sensor_thread", interval=1)
        self.threads["start_sensor_thread"] = self.start_sensor_thread
        self.threads["start_sensor_thread"].start()
    
    def _start_sensor_func(self):
        self.add_task2queue(self.procs_name["sensor"], {"cmd":"read_sensor", "from": self.name})

    def thread_cleanup(self):
        # self.initiate_shutdown()
        # self.threads["start_sensor_thread"].stop()
        self.logger.info(f"MainThread {self.name} send shutdown signal to other threads...")
        for thread_name, thread in self.threads.items():
            thread.stop()
            thread.join()
        


if __name__ == "__main__":
    FILE_PATH = os.path.join(current_dir, "log/myapp.log")
    edge_app = EdgeApp(log_level="info", log_path=FILE_PATH)
    edge_app.run()
