import sys
import os

# add the parent directory of the current file to the system path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir =  os.path.dirname(os.path.dirname(current_dir))
sys.path.append(parent_dir)

from templates.threadman.sys_thread import SysThread



class DataProcessThread(SysThread):
    def __init__(self, name, logger, sys_queues, parent, event):
        super().__init__(name, logger, sys_queues, parent=parent, event=event)        
        
    def command_register(self):
        super().command_register()
        self.cmd_dispatcher.register_handler("process_data", self.handle_process_data_command)

    def handle_process_data_command(self, *args, **kwargs):
        task = kwargs["task"]
        data = task["data"]["val"]
        time_stamp = task["data"]["time"]
        # process the data (for example, by multiplying it by 2)
        processed_data = data * 2
        self.logger.info(f"Processed data: {processed_data}")
        self.add_task2queue("database", {"cmd": "insert", "table": "sensor_data",
                                        "data": (time_stamp, processed_data), "from": self.name})

    def thread_cleanup(self):
        self.logger.info(f"Thread {self.name} cleaned up")
        # Disconnect from sensor