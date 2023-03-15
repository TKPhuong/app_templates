import time
from datetime import datetime
import sys
import os
import random


# add the parent directory of the current file to the system path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir =  os.path.dirname(os.path.dirname(current_dir))
sys.path.append(parent_dir)

from templates.threadman.sys_thread import SysThread
from templates.utils.helper_funcs.display_time import timestamp2str
from templates.system.status import StatusTracker


class SensorThread(SysThread):
    def __init__(self, name, logger, sys_queues, parent, event, initial_statuses:dict):
        super().__init__(name, logger, sys_queues, parent=parent, event=event)  
        # StatusTrackerの初期化
        self.stats_tracker = StatusTracker(id=self, initial_status=initial_statuses)   

    def command_register(self):
        super().command_register()
        self.cmd_dispatcher.register_handler("read_sensor", self.handle_read_sensor_command)

    def handle_read_sensor_command(self, *args, **kwargs):
        task = kwargs["task"]
        # simulate reading from a sensor
        value = random.random() * 100
        self.logger.info(f"Sensor read value = {value}")
        # time_stamp = datetime.now()
        time_stamp = timestamp2str(time.time())
        self.add_task2queue("data_process", {"cmd": "process_data", 
                            "data": {"time":time_stamp, "val":value}, "from": self.name})
