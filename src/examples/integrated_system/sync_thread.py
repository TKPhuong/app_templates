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
from templates.comm.tcp_com import TcpClient
from edge_tcp_server import EdgeTcpServer


class EdgeSynchronizeThread(SysThread):
    def __init__(self, name, logger, sys_queues, parent, event=None, comm_info=None, *args, **kwargs):
        super().__init__(name, logger, sys_queues, parent=parent, event=event)
        self.comm_info = comm_info
        self.tcp_server = None
        self.tcp_client = None
        self.server_watchdog_thread = None

    def command_register(self):
        super().command_register()
        self.cmd_dispatcher.register_handler("request_data", self.handle_request_data_command)
        self.cmd_dispatcher.register_handler("send_data", self.handle_send_data_command)

    def thread_initiate(self):
        super().thread_initiate()
        # Create TCP server
        self.tcp_server = EdgeTcpServer(
            self.logger.getChild("EdgeTcpServer"),
            self.comm_info["own"]["ip"],
            self.comm_info["own"]["port"],
            self.comm_info["main"]["ip"],
            self.comm_info["main"]["port"],
            sync_handler=self,
        )
        # Start TCP server as a seperate thread
        self.tcp_server.start(as_thread=True)
        # Start TCP client
        self.tcp_client = TcpClient(self.logger.getChild("TcpClient"),
                                     self.comm_info["main"]["ip"],
                                       self.comm_info["main"]["port"])
        self.server_watchdog_thread = FuncThread(target=self._server_health_check, 
                                                name=f"{self.name}.server_watchdog", 
                                                interval=5)
        self.server_watchdog_thread.start()

    def handle_request_data_command(self, *args, **kwargs):
        task = kwargs["task"]
        # Get data from the database
        self.get_data()

    def handle_send_data_command(self, *args, **kwargs):
        task = kwargs["task"]
        # send data to main system
        self.send_data_to_main_system(task["data"])

    def thread_cleanup(self):
        super().thread_cleanup()
        # Stop Watchdog Thread
        if self.server_watchdog_thread:
            self.server_watchdog_thread.stop()
            self.server_watchdog_thread.join()

        # Stop TCP server
        if self.tcp_server:
            self.tcp_server.stop()
            self.tcp_server = None

    def get_data(self):
        # send get_data command to DBThread
        self.add_task2queue("database", {"cmd": "get_data", "edge_name": self.name, "from": self.name})

    def send_data_to_main_system(self, data):
        # Send data to main system using TCP client
        self.tcp_client.send_data(data)
        # Log sent data
        self.logger.info(f"Sent data to main system: {data}")

    def _server_health_check(self):
        if self.tcp_server.thread.is_alive():
            self.logger.info(f"Server_Health_Check - STATUS=OK")
        else:
            self.logger.info(f"Server is down. Restarting server...")
            if self.server_watchdog_thread:
                self.server_watchdog_thread.stop()
                self.server_watchdog_thread.join()

            self.thread_initiate()


