import logging
import time
from datetime import datetime
import sys
import os
import queue

# add the parent directory of the current file to the system path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from templates.threadman.func_thread import FuncThread

class SensorThread(FuncThread):
    def __init__(self, name, sensor_log, data_queue, *args, **kwargs):
        super().__init__(name, sensor_log, *args, **kwargs)
        self.data_queue = data_queue
        self.sensor_log = sensor_log

    def thread_initiation(self):
        self.logger.info("SensorThread initialized")
        # Connect to sensor

    def process_task(self, task):
        # Read sensor data
        sensor_data = 1.0  # Simulating sensor data
        self.data_queue.put(sensor_data)
        self.logger.info(f"Sensor data read: {sensor_data}")
        time.sleep(1)

    def thread_cleanup(self):
        self.logger.info("SensorThread cleaned up")
        # Disconnect from sensor


class DataProcessThread(FuncThread):
    def __init__(self, name, process_log, data_queue, output_queue, *args, **kwargs):
        super().__init__(name, process_log, *args, **kwargs)
        self.data_queue = data_queue
        self.output_queue = output_queue

    def process_task(self, task):
        # Process sensor data
        processed_data = task * 2  # Simulating data processing
        self.logger.info(f"Data processed: {processed_data}")
        self.output_queue.put(processed_data)


class UIThread(FuncThread):
    def __init__(self, name, ui_log, data_queue, result_queue, *args, **kwargs):
        super().__init__(name, ui_log, *args, **kwargs)
        self.data_queue = data_queue
        self.result_queue = result_queue

    def process_task(self, task):
        """Display input and output data"""
        if task == "display":
            # display input data
            input_data = self.data_queue.get()
            self.logger.info(f"Input data: {input_data}")
            self.data_queue.task_done()
            
            # display output data
            output_data = self.result_queue.get()
            self.logger.info(f"Output data: {output_data}")
            self.result_queue.task_done()


class PlcThread(FuncThread):
    def __init__(self, name, plc_log, sys_queue, *args, **kwargs):
        super().__init__(name, plc_log, sys_queue, *args, **kwargs)
        # Additional initialization specific to PlcThread
        self.plc = PLC() # Initialize PLC object
        self.actions = {
            'start': self.plc.start,
            'stop': self.plc.stop,
            'pause': self.plc.pause,
            # Define more actions as needed
        }

    def process_task(self, task):
        # Task is assumed to be a dictionary with 'type' and 'data' keys
        if task['type'] == 'output':
            output_data = task['data']
            # Perform action based on output data
            if output_data in self.actions:
                action = self.actions[output_data]
                action() # Call the corresponding action function
            else:
                self.logger.warning(f"Invalid output data: {output_data}")


class PLC:
    def __init__(self):
        self.is_running = False
        self.is_paused = False

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            # Start the PLC

    def stop(self):
        if self.is_running:
            self.is_running = False
            self.is_paused = False
            # Stop the PLC

    def pause(self):
        if self.is_running and not self.is_paused:
            self.is_paused = True
            # Pause the PLC


class MainApp:
    def __init__(self, 
                comm_info={
                            "main":{"ip":"localhost", "port":5000},
                            "edges":{
                                    "edge1":{"ip":"localhost", "port":5001},
                                    "edge2":{"ip":"localhost", "port":5002},
                            }
                }
    ):  
        # Save communication info to instance
        self.comm_info = comm_info
        # Initialize logger
        self.logger = logging.getLogger("MainApp")
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.procs_name = {"sync": "sync",
                        "display":"display", "db":"database"}
        
        # Create queues
        self.queues = {v: queue.Queue() for k,v in self.procs_name}

        # Create threads
        self.display_thread = DisplayThread(
            self.procs_name["display"], 
            self.logger.getChild(self.procs_name["display"]), 
            self.queues
        )
        self.sync_thread = SynchronizeThread(
            self.procs_name["sync"], 
            self.logger.getChild(self.procs_name["sync"]), 
            self.queues,
            comm_info=self.comm_info
        )
        self.db_thread = DBThread(
            self.procs_name["db"], 
            self.logger.getChild(self.procs_name["db"]), 
            self.queues
        )

        # Start threads
        self.sync_thread.start()
        self.display_thread.start()
        self.db_thread.start()


    def run(self):
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.logger.info("Stopping threads...")
            # Stop threads
            self.sync_thread.stop()
            self.display_thread.stop()
            self.db_thread.stop()


class EdgeApp:
    def __init__(self, 
                comm_info={
                            "main":{"ip":"localhost", "port":5000},
                            "own":{"ip":"localhost", "port":5001}
                }
    ):  
        
        # Save communication info to instance
        self.comm_info = comm_info
        # Initialize logger
        self.logger = logging.getLogger("EdgeApp")
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.procs_name = {"sensor": "sensor", "process":"data_process",
                                "sync":"sync", "db":"database"}
        
        # Create queues
        self.queues = {v: queue.Queue() for k,v in self.procs_name}

        # Create threads
        self.sensor_thread = SensorThread(
            self.procs_name["sensor"], 
            self.logger.getChild(self.procs_name["sensor"]), 
            self.queues
        )
        self.processing_thread = DataProcessThread(
            self.procs_name["process"], self.logger,
            self.logger.getChild(self.procs_name["process"]),  
            self.queues
        )
        self.sync_thread = SynchronizeThread(
            self.procs_name["sync"], 
            self.logger.getChild(self.procs_name["sync"]), 
            self.queues,
            comm_info=self.comm_info,
        )
        self.db_thread = DBThread(
            self.procs_name["db"], 
            self.logger.getChild(self.procs_name["db"]), 
            self.queues
        )

        # Start threads
        self.sensor_thread.start()
        self.processing_thread.start()
        self.db_thread.start()
        self.sync_thread.start()

    def run(self):
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.logger.info("Stopping threads...")
            # Stop threads
            self.sensor_thread.stop()
            self.processing_thread.stop()
            self.db_thread.stop()
            self.sync_thread.stop()


if __name__ == "__main__":
    app = App()
    app.run()