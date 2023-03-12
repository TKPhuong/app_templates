import tempfile
import os
import sys

# add the parent directory of the current file to the system path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir =  os.path.dirname(os.path.dirname(current_dir))
sys.path.append(parent_dir)

from templates.threadman.sys_thread import SysThread
from templates.utils.helper_funcs.display_time import timestamp2str
from templates.utils.log_tools.logger import Logger
from templates.comm.tcp_com import TcpClient, TcpServer


if __name__ == "__main__":
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Use the temporary directory
        log_path = os.path.join(temp_dir, "myapp.log")
        logger = Logger(name="sample_client", level="debug", file_path=log_path, backup_count=7)
        logger.info(f"Temporary log file created at {log_path}")
        client = TcpClient(logger, "localhost", 5001)
        result = client.send_data({"cmd":"CMD_REQUEST"})
        logger.info(f"result: {result}")