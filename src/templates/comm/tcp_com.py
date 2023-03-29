import socket
import json
from typing import Callable
import threading
import time
import logging

class CmdDispatcher:
    
    def __init__(self):
        """
        初期化関数。ハンドラディクショナリーを初期化する。
        """
        self._handlers = {}

    def register_handler(self, event: str, handler: Callable):
        """
        イベントとハンドラを紐付ける登録関数。

        Parameters
        ----------
        event : str
            イベント名
        handler : Callable
            イベント時に呼ばれる関数
        """
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(handler)

    def dispatch(self, event: str, instance, *args, **kwargs):
        """
        イベントに対応した各ハンドラを呼び出す関数。

        Parameters
        ----------
        event : str
            イベント名
        instance : object
            この処理を持つクラスのインスタンス
        *args : 
            ハンドラにわたす引数可変長個数の引数
        **kwargs : 
            ハンドラにわたすキーワード引数可変長個数の引数
        """
        try:
            for handler in self._handlers[event]:
                handler(instance, *args, **kwargs)
        except KeyError as e:
            e.args = (f"イベント {event} に対応するハンドラが登録されていません。", )
            raise e


class TcpServer:
    
    def __init__(self, logger, source_ip, source_port, dest_ip, dest_port, sync_handler=None):
        """
        TcpServerクラスの初期化関数。

        Parameters
        ----------
        logger : logging.Logger
            ロガーインスタンス
        source_ip : str
            ソースIPアドレス
        source_port : int
            ソースポート番号
        dest_ip : str
            宛先IPアドレス
        dest_port : int
            宛先ポート番号
        sync_handler : Callable or None
            非同期で実行したい場合に指定するハンドラ
        """
        self.name = logger.name
        self.logger = logger
        self.source_address = (source_ip, source_port)
        self.dest_address = (dest_ip, dest_port)
        self.breakpoint = False
        self.sync_handler = sync_handler
        self.server_socket = None
        self.cmd_dispatcher = CmdDispatcher()

    def server_initiate(self):
        """
        TCPサーバーを初期化する関数。
        """
        self.logger.info("TCPサーバーの初期化を行う...")
        self.breakpoint = False
        self.command_register()
        
    def command_register(self):
        """
        継承時に、定義した処理に紐づくハンドラを登録する関数。
        """
        self.cmd_dispatcher.register_handler("CMD_EXAMPLE", self.handle_example_command)

    def start(self, as_thread=True):
        """
        サーバーをスタートする関数。

        Parameters
        ----------
        as_thread : bool
            Threadを使用するか否か。デフォルトはTrueで使用する。
        """
        if as_thread:
            self.thread = threading.Thread(target=self.run, name=self.name)
            self.thread.start()
            return self.thread
        else:
            self.run()
    
    def run(self):
        """
        サーバーを立ち上げて接続を受け付ける関数。
        """
        try:
            self.server_initiate()
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.bind(self.source_address)
                server_socket.listen(1)
                self.server_socket = server_socket
                self.logger.info(f"サーバーは{self.source_address[0]}:{self.source_address[1]}で稼働しています。")

                while True:
                    connection, client_address = server_socket.accept()
                    self.logger.info(f"New Connection : {client_address}")
                    self.handle_connection(connection)

                    if self.breakpoint:
                        break
        except OSError as e:
            if not self.breakpoint:
                self.logger.error(f"サーバーが起動できませんでした -{e}")
            else:
                pass
        finally:
            self.logger.warning("サーバーは停止しました。")


    def stop(self):
        """
        サーバーを停止する関数。
        """
        self.logger.info("サーバーを停止しています...")
        self.breakpoint = True
        while True:
            if self.server_socket:
                break
            else:
                pass
        
        self.server_socket.close()

    def handle_connection(self, connection):
        """
        接続時に行う処理を管理する関数。

        Parameters
        ----------
        connection : socket.connection
            クライント側のソケットコネクション
        """
        try:
            data = connection.recv(4096).decode('utf-8')
            self.logger.info(f"データ取得 : {data}")
            data_dict = json.loads(data)

            command = data_dict.get("cmd")
            self.cmd_dispatcher.dispatch(command, instance=self, connection=connection, data_dict=data_dict)

        except OSError as e:
            self.logger.error(f"クライアントとの通信時にエラーが発生しました: {e}")
        except json.JSONDecodeError as e:
            self.logger.error(f"JSONデータのデコード中にエラーが発生しました: {e}")
        except Exception as e:
            self.logger.error(f"クライアントとの通信時に予期せぬエラーが発生しました: {e}")
        finally:
            connection.close()
            # self.stop()

    #TcpServerを継承するとき、適切な処理を以下の形でクラスに追加する
    def handle_example_command(self, *args, **kwargs):
        """
        「コマンド名」を受信したときの処理を行う関数。
        kwargsに受信した接続と受信したデータを格納される。

        Parameters
        ----------
        *args : 
            使用しない。
        **kwargs : 
            connectionとdata_dictをkeyとした辞書。
        """
        connection = kwargs["connection"]
        data_dict = kwargs["data_dict"]
        #処理を書く
        ...
    

class TcpClient:
    
    def __init__(self, logger, server_ip, server_port):
        """
        TcpClientクラスの初期化関数。

        Parameters
        ----------
        logger : logging.Logger
            ロガーインスタンス
        server_ip : str
            サーバーのIPアドレス
        server_port : int
            サーバーのポート番号
        """
        self.logger = logger
        self.server_address = (server_ip, server_port)

    def send_data(self, data):
        """
        サーバーにデータを送信する関数。

        Parameters
        ----------
        data : dict
            送信するJSONデータ
            
        Returns
        -------
        response.get('result', None) : Any
            成功した場合は、実行結果を返す。失敗した場合はNoneを返す。
        """
        try:
            # TCPソケットを作成し、サーバーに接続
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect(self.server_address)

                # コマンドを含む辞書を作成し、JSONフォーマットにエンコードする
                json_data = json.dumps(data).encode('utf-8')

                # JSONデータをサーバーに送信する
                client_socket.sendall(json_data)

                # サーバーからの応答を受信し、JSON形式からデコードする
                response_data = client_socket.recv(4096).decode('utf-8')
                response = json.loads(response_data)

                # レスポンスを処理する
                if response.get('success'):
                    self.logger.info("コマンドの送信が成功しました。")
                    return response.get('result', None)
                else:
                    self.logger.warning("コマンドの送信が失敗しました。")
                    return None

        except OSError as e:
            self.logger.error(f"サーバーとの通信エラー: {e}")
        except json.JSONDecodeError as e:
            self.logger.error(f"JSONデータのデコードエラー: {e}")
        except Exception as e:
            self.logger.error(f"サーバーとの通信時に予期せぬエラーが発生しました: {e}")

        return None
    


if __name__ == "__main__":
    import time

    # TcpServerを継承したカスタムサーバークラス
    class CustomServer(TcpServer):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def command_register(self):
            super().command_register()
            self.cmd_dispatcher.register_handler("CUSTOM_COMMAND", self.handle_custom_command)

        def handle_custom_command(self, *args, **kwargs):
            connection = kwargs["connection"]
            data_dict = kwargs["data_dict"]
            self.logger.info(f"カスタムコマンドを受信: {data_dict}")
            response = {"success": True, "result": "カスタムコマンドが実行されました"}
            json_response = json.dumps(response).encode('utf-8')
            connection.sendall(json_response)

    # ロガーを初期化する
    logger = logging.getLogger("CustomServer")
    logging.basicConfig(level=logging.DEBUG)

    # カスタムサーバーを初期化して起動する
    custom_server = CustomServer(logger, "127.0.0.1", 5000, "127.0.0.1", 5001)
    custom_server.start(as_thread=True)

    # TcpClientを初期化する
    client = TcpClient(logger, "127.0.0.1", 5000)

    # サーバーの起動を待つ
    time.sleep(2)

    # カスタムコマンドをサーバーに送信する
    command_data = {"cmd": "CUSTOM_COMMAND", "data": "Some data"}
    result = client.send_data(command_data)
    logger.info(f"サーバーからの応答: {result}")

    # カスタムサーバーを停止する
    custom_server.stop()