import socket
import json
from typing import Callable
import threading
import time

class CmdDispatcher:
    def __init__(self):
        self._handlers = {}

    def register_handler(self, event: str, handler: Callable):
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(handler)

    def dispatch(self, event: str, instance, *args, **kwargs):
        try:
            # instance.logger.debug(f"self._handlers[event]={self._handlers[event]}")
            for handler in self._handlers[event]:
                handler(instance, *args, **kwargs)
        except KeyError as e:
            e.args = (f"There is no handler registered for event {event}", )
            raise e


class TcpServer:
    
    def __init__(self, logger, source_ip, source_port, dest_ip, dest_port, sync_handler=None):
        self.name = logger.name
        self.logger = logger
        self.source_address = (source_ip, source_port)
        self.dest_address = (dest_ip, dest_port)
        self.breakpoint = False
        self.sync_handler = sync_handler
        self.server_socket = None
        self.cmd_dispatcher = CmdDispatcher()

    def server_initiate(self):
        self.logger.info("TCPサーバーの処理化を行う...")
        self.command_register()
        
    #TcpServerを継承するとき、各コマンドに定義した処理を登録する
    def command_register(self):
        self.cmd_dispatcher.register_handler("CMD_EXAMPLE", self.handle_example_command)
        ...

    def start(self, as_thread=True):
        if as_thread:
            self.thread = threading.Thread(target=self.run, name=self.name)
            self.thread.start()
            return self.thread
        else:
            self.run()
    
    def run(self):
        try:
            self.server_initiate()
            # Create a TCP socket and bind it to the server address and port
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.bind(self.source_address)
                server_socket.listen(1)
                # handler to stop the server
                self.server_socket = server_socket
                self.logger.info(f"Server is running on {self.source_address[0]}:{self.source_address[1]}")

                # Wait for incoming client connections
                while True:
                    connection, client_address = server_socket.accept()
                    self.logger.info(f"Connected by {client_address}")
                    self.handle_connection(connection)

                    if self.breakpoint:
                        break
        except OSError as e:
            self.logger.error(f"Server could not be started or get terminated -{e}")
        finally:
            self.logger.warning("Server Stopped !")


    def stop(self):
        """
        Stops the server.
        """
        self.logger.info("Stopping server...")
        self.breakpoint = True
        while True:
            if self.server_socket:
                break
            else:
                pass
        
        self.server_socket.close()

    def handle_connection(self, connection):
        try:
            # Receive data from the client
            data = connection.recv(4096).decode()
            self.logger.info(f"Received: {data}")

            # Decode the JSON data received
            data_dict = json.loads(data)

            # Handle the incoming command
            command = data_dict.get("cmd")
            self.cmd_dispatcher.dispatch(command, instance=self, connection=connection, data_dict=data_dict)

        except OSError as e:
            self.logger.error(f"Error handling client connection: {e}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON data: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error handling client connection: {e}")
        finally:
            connection.close()
            # self.stop()

    #TcpServerを継承するとき、適切な処理を以下の形でクラスに追加する
    def handle_example_command(self, *args, **kwargs):
        #「コマンド名」を受信したときの処理。kwargsに受信した接続と受信したデータを格納される
        connection = kwargs["connection"]
        data_dict = kwargs["data_dict"]
        #処理を書く
        ...
    

class TcpClient:

    def __init__(self, logger, server_ip, server_port):
        self.logger = logger
        self.server_address = (server_ip, server_port)

    def send_data(self, data):
        try:
            # Create a TCP socket and connect to the server
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect(self.server_address)

                # Create a dictionary containing the command and encode it in JSON format
                json_data = json.dumps(data).encode()

                # Send the JSON data to the server
                client_socket.sendall(json_data)

                # Receive the response from the server and decode it from JSON
                response_data = client_socket.recv(4096).decode()
                response = json.loads(response_data)

                # Handle the response
                if response.get('success'):
                    self.logger.info("Command executed successfully")
                    return response.get('result', None)
                else:
                    self.logger.warning("Command execution failed")
                    return None

        except OSError as e:
            self.logger.error(f"Error communicating with server: {e}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON data: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error communicating with server: {e}")

        return None