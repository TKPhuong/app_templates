import time
import sys
import os


# add the parent directory of the current file to the system path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir =  os.path.dirname(os.path.dirname(current_dir))
sys.path.append(parent_dir)

from templates.threadman.func_thread import FuncThread
from templates.threadman.sys_thread import SysThread
from templates.databases import SqliteDB


class EdgeDBThread(SysThread):
    def __init__(self, name:str, logger, sys_queues, parent, event=None, db_file:str="sensor_data.db"):
        super().__init__(name, logger, sys_queues, parent=parent, event=event)
        self.db_file = db_file

        self.db = None
        self.tables = ["sensor_data"]
        self.last_sent_index = 0  # initialize index of last sent data

    def command_register(self):
        super().command_register()
        self.cmd_dispatcher.register_handler("insert", self.handle_insert_command)
        self.cmd_dispatcher.register_handler("get_data", self.handle_get_data_command)

    def thread_initiate(self):
        super().thread_initiate()

        # create database file if it does not exist
        if not os.path.isfile(self.db_file):
            open(self.db_file, 'w').close()

        # create database connection
        self.db = SqliteDB(self.db_file)

        # create tables if they do not exist
        for table in self.tables:
            self.db.add_table(table, [("timestamp", "DATETIME"), ("data", "FLOAT")])

    def handle_insert_command(self, *args, **kwargs):
        task = kwargs["task"]
        data = task["data"]
        self.db.insert(task["table"], data)

    def handle_get_data_command(self, *args, **kwargs):
        task = kwargs["task"]
        # Start a thread of self.get_data to get 5 records of data from database
        self.get_data_thread = FuncThread(target=self.get_data, name=f"{self.name}.get_data")
        self.get_data_thread.start()

    def thread_cleanup(self):
        super().thread_cleanup()
        if self.db:
            self.db = None

    def get_data(self):
        # If the accumulated data is not enough (5 records), since last send, wait until get enough data and send back to EdgeSynchronizeThread
        while True:
            # count the number of records since last sent index
            # ROWID approach
            # record_count = self.db.select(
            #     "sensor_data",
            #     columns=["COUNT(*)"],
            #     where_clause=f"ROWID > {self.last_sent_index}",
            # )
            # record_count = record_count[0][0] if record_count else 0

            # Timestamp Approach
            record_count = self.db.select(
                "sensor_data",
                columns=["COUNT(*)"],
                where_clause=f'timestamp > "{self.last_sent_index}"',
            )
            record_count = record_count[0][0] if record_count else 0
            # if there are not enough records, wait for 1 second and try again
            if record_count < 5:
                self.logger.info(f"Not enough records since last sent index. Check again after 1 second.")
                time.sleep(1)
            else:
                # break out of the loop since we have sent the required number of records
                break

        # get 5 records of unsent data since last sent data index
        data = self.db.select(
            "sensor_data",
            columns=["timestamp", "data"],
            where_clause=f'timestamp > "{self.last_sent_index}"',
            order_by="timestamp ASC",
            limit=5,
        )

        # send data to EdgeSynchronizeThread for sending to main system
        self.add_task2queue("sync", {"cmd": "send_data", "data": data, "from": self.name})

        # update the sent data index
        self.last_sent_index = data[-1][0]
        self.logger.info(f"Update last sent index = {self.last_sent_index}")