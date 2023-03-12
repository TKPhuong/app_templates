import sys
import os
import json

# add the parent directory of the current file to the system path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir =  os.path.dirname(os.path.dirname(current_dir))
sys.path.append(parent_dir)

from templates.comm.tcp_com import TcpServer


class EdgeTcpServer(TcpServer):
    
    def command_register(self):
        self.cmd_dispatcher.register_handler("CMD_REQUEST", self.handle_request_command)
    
    def handle_request_command(self, *args, **kwargs):
        connection = kwargs["connection"]
        data_dict = kwargs["data_dict"]
        try:
            self.logger.info("Handling CMD_REQUEST command...")
            task = {"cmd": "request_data", "from": self.name}
            self.sync_handler.task_queue.put(task)
            # Encode the response data as JSON string
            response_dict = {"success": True}
            response_json = json.dumps(response_dict)
            # Send a response back to the client
            connection.sendall(response_json.encode("UTF-8"))
        except Exception as e:
            self.logger.info(f"Error handling CMD_REQUEST command: {e}")