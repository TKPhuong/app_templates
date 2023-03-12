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
from templates.comm.tcp_com import TcpClient, TcpServer
from templates.databases import SqliteDB

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
        self.logger.info(f"Thread {self.name} send shutdown signal to other threads...")
        for thread_name, thread in self.threads.items():
            thread.stop()
            thread.join()
        self.logger.info(f"Program {self.name} exited...")
        


# class MainSynchronizeThread(SysThread):
#     def __init__(self, name:str, logger, sys_queues, event, comm_info:Dict[str,Any]):
#         super().__init__(name, logger, sys_queues, event=event)
#         self.comm_info = comm_info
#         self.edge_data = {}
#         self.tcp_clients = {}
#         self.tcp_servers = {}
#         self.sync_interval = 5

#     def thread_initiate(self):
#         super().thread_initiate()
#         self.logger.info(f"{self.name} started")
#         # Connect to all edge devices
#         for edge_name, edge_info in self.comm_info["edges"].items():
#             self.tcp_clients[edge_name] = TcpClient(edge_info["ip"], edge_info["port"])

#         # Start TCP servers
#         self.tcp_servers["main"] = TcpServer(self.comm_info["main"]["ip"], self.comm_info["main"]["port"], None, None, self)
#         self.tcp_servers["main"].start()

#         for edge_name, edge_info in self.comm_info["edges"].items():
#             self.tcp_servers[edge_name] = TcpServer(edge_info["ip"], edge_info["port"], self.comm_info["main"]["ip"], self.comm_info["main"]["port"], self)
#             self.tcp_servers[edge_name].start()

#     def process_task(self, task):
#         pass

#     def update_data(self, data):
#         """
#         Updates the edge data dictionary with the given data.

#         Args:
#             data: A dictionary containing data from an edge device.
#         """
#         self.edge_data[data["edge"]] = data["data"]
#         self.logger.info(f"Updated edge data: {self.edge_data}")

#     def get_data(self, edge_name):
#         """
#         Returns data for a specific edge device.

#         Args:
#             edge_name: The name of the edge device.

#         Returns:
#             A JSON string containing the edge device's data.
#         """
#         if edge_name in self.edge_data:
#             return json.dumps(self.edge_data[edge_name])
#         else:
#             return ""

#     def thread_cleanup(self):
#         self.logger.info(f"{self.name} stopped")
#         # Stop TCP servers
#         for server in self.tcp_servers.values():
#             server.stop()

#         # Disconnect from all edge devices
#         for client in self.tcp_clients.values():
#             client.disconnect()

# class DisplayThread(SysThread):
#     ...


# class MainApp(SysThread):
#     def __init__(self, 
#                 name="main_sys",
#                 comm_info={
#                             "main":{"ip":"localhost", "port":5000},
#                             "edges":{
#                                     "edge1":{"ip":"localhost", "port":5001},
#                                     "edge2":{"ip":"localhost", "port":5002},
#                             }
#                 }
#     ):  
#         # Save App name
#         self.name = name
#         # Save communication info to instance
#         self.comm_info = comm_info
#         # Initialize logger
#         self.logger = logging.getLogger("MainApp")
#         self.logger.setLevel(logging.INFO)
#         handler = logging.StreamHandler(sys.stdout)
#         formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
#         handler.setFormatter(formatter)
#         self.logger.addHandler(handler)
#         self.procs_name = {
#                             "main": self.name,
#                             "sync": "sync",
#                             "display":"display",
#                             "db":"database"
#                             }
        
        
#         # Create queues
#         self.queues = {v: queue.Queue() for k,v in self.procs_name}
#         self.task_queue = self.queues["main"]
#         super().__init__(name, self.logger, self.queues)

#         # Create event handlers
#         self.thread_handlers = {v: threading.Event() for k,v in self.procs_name if k != "main"}

#         # Create threads
#         self.display_thread = DisplayThread(
#             self.procs_name["display"], 
#             self.logger.getChild(self.procs_name["display"]), 
#             self.queues,
#             self.thread_handlers["display"],
#         )
#         self.sync_thread = MainSynchronizeThread(
#             self.procs_name["sync"], 
#             self.logger.getChild(self.procs_name["sync"]), 
#             self.queues,
#             self.thread_handlers["sync"],
#             comm_info=self.comm_info
#         )
#         self.db_thread = DBThread(
#             self.procs_name["db"], 
#             self.logger.getChild(self.procs_name["db"]), 
#             self.queues,
#             self.thread_handlers["db"],
#         )

#     def pause_thread(self, thread_name):
#         self.thread_handlers[thread_name].clear()
#         self.logger.info(f"Thread {self.name} paused")

#     def resume_thread(self, thread_name):
#         self.thread_handlers[thread_name].set()
#         self.logger.info(f"Thread {self.name} resumed")

#     def thread_initiate(self):
#         # Start threads
#         self.sync_thread.start()
#         self.display_thread.start()
#         self.db_thread.start()

#     def process_task():
#         pass

#     def thread_cleanup(self):
#         self.stop()
#         self.logger.info(f"Program {self.name} exited...")

    # def run(self):
    #     try:
    #         self.initiate()
    #         while True:
    #             try:
    #                 task = self.task_queue.get(timeout=1)
    #                 if task is None:
    #                     break
    #                 self.process_task(task)
    #                 self.task_queue.task_done()
    #             except queue.Empty:
    #                 pass
    #     except KeyboardInterrupt:
    #         pass
    #     except Exception as e:
    #         self.logger.error(f"Program {self.name} error: {e}")
    #     finally:
    #         self.logger.info("Stopping threads...")
    #         # Stop threads
    #         self.sensor_thread.stop()
    #         self.processing_thread.stop()
    #         self.db_thread.stop()
    #         self.sync_thread.stop()
    #         self.logger.info(f"Program {self.name} exited...")

if __name__ == "__main__":
    FILE_PATH = os.path.join(current_dir, "log/myapp.log")
    edge_app = EdgeApp(log_level="info", log_path=FILE_PATH)
    edge_app.run()
