import pytest
import socket
import os
import sys
import time
import json
# このファイルの親ディレクトリをシステムパスに追加する
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from templates.comm.tcp_com import TcpServer, TcpClient
from templates.utils.log_tools import Logger

class CustomTcpServer(TcpServer):
    def command_register(self):
        super().command_register()
        self.cmd_dispatcher.register_handler("CMD_TEST", self.handle_test_command)

    def handle_test_command(self, *args, **kwargs):
        connection = kwargs["connection"]
        response = {"success": True, "result": "Test command executed successfully"}
        connection.sendall(json.dumps(response).encode())

class TestTcpCommunication:

    @pytest.fixture(scope="module")
    def logger(self):
        return Logger("test_tcpclient")

    @pytest.fixture(scope="module")
    def server_thread(self):
        logger = Logger("test_tcpserver")
        server = CustomTcpServer(logger, "127.0.0.1", 5000, "127.0.0.1", 5000)
        thread = server.start(as_thread=True)
        time.sleep(1)
        yield thread
        server.stop()

    def test_server_startup(self, server_thread):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = s.connect_ex(('127.0.0.1', 5000))
        assert result == 0

    def test_send_command(self, server_thread, logger):
        client = TcpClient(logger, "127.0.0.1", 5000)
        data = {"cmd": "CMD_TEST"}
        response = client.send_data(data)
        assert response == "Test command executed successfully"

    def test_invalid_command(self, server_thread, logger):
        client = TcpClient(logger, "127.0.0.1", 5000)
        data = {"cmd": "INVALID_CMD"}
        response = client.send_data(data)
        expected_response = {"invalid_cmd": True, "msg":"コマンドINVALID_CMDが登録されていません。"}
        assert response == expected_response
