import socket

class TcpServer:
    """
    A server class for synchronizing data with a remote client.

    Args:
        source_ip (str): The IP address of the server.
        source_port (int): The port number of the server.
        dest_ip (str): The IP address of the client.
        dest_port (int): The port number of the client.
    """

    def __init__(self, source_ip, source_port, dest_ip, dest_port):
        self.source_address = (source_ip, source_port)
        self.dest_address = (dest_ip, dest_port)
        self.breakpoint = False

    def start(self):
        """
        Starts the server and listens for incoming client connections.
        """
        try:
            # Create a TCP socket and bind it to the server address and port
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.bind(self.source_address)
                server_socket.listen(1)
                print(f"Server is running on {self.source_address[0]}:{self.source_address[1]}")

                # Wait for incoming client connections
                while True:
                    connection, client_address = server_socket.accept()
                    print(f"Connected by {client_address}")
                    self.handle_connection(connection)

                    if self.breakpoint:
                        print("Server Stopped !")
                        break
        except OSError as e:
            print(f"Could not start server: {e}")
    
    def stop(self):
        """
        Stops the server.
        """
        print("Stopping server...")
        self.breakpoint = True

    def handle_connection(self, connection):
        """
        Handles an incoming client connection.

        Args:
            connection (socket): The socket object representing the client connection.
        """
        try:
            # Receive data from the client
            data = connection.recv(4096).decode()
            print(f"Received: {data}")

            # Handle the incoming command
            command = data.split(",")
            if command[0] == "CMD_WORK_HISTORY":
                self.handle_work_history_command(command[2:])
            elif command[0] == "CMD_ERROR_STATUS":
                self.handle_error_status_command(command[1:])
            elif command[0] == "CMD_REBOOT":
                self.handle_reboot_command()
            elif command[0] == "CMD_HEALTH":
                self.handle_health_command()
            else:
                print(f"Ignoring unknown command: {command}")

            # Send a response back to the client
            connection.sendall(b"SUCCESS")
        except OSError as e:
            print(f"Error handling client connection: {e}")
        except Exception as e:
            print(f"Unexpected error handling client connection: {e}")
        finally:
            connection.close()

    def handle_work_history_command(self, data):
        """
        Handles the CMD_WORK_HISTORY command.

        Args:
            data (list): The data sent with the command.
        """
        try:
            print("Handling CMD_WORK_HISTORY command...")
            predict = [field.replace("[", "").replace("]", "").replace(" ", "") for field in data]
            # TODO: Do something with the data
        except Exception as e:
            print(f"Error handling CMD_WORK_HISTORY command: {e}")

    def handle_error_status_command(self, data):
        """
        Handles the CMD_ERROR_STATUS command.

        Args:
            data (list): The data sent with the command.
        """
        try:
            print(f"Handling CMD_ERROR_STATUS command: {data}")
            # TODO: Do something with the data
        except Exception as e:
            print(f"Error handling CMD_ERROR_STATUS command: {e}")

    def handle_reboot_command(self):
        """
        Handles the CMD_REBOOT command.
        """
        try:
            print("Handling CMD_REBOOT command...")
            # TODO: Replace the following line with code that actually reboots the system
            print("Rebooting system...")
        except Exception as e:
            print(f"Error handling CMD_REBOOT command: {e}")

    def handle_health_command(self):
        """
        Handles the CMD_HEALTH command.
        """
        try:
            print("Handling CMD_HEALTH command...")
            # TODO: Replace the following line with code that sends a health status to the client
            print("Sending health status...")
        except Exception as e:
            print(f"Error handling CMD_HEALTH command: {e}")


class TcpClient:
    """
    A client class for interacting with a TcpServer.

    Args:
        server_ip (str): The IP address of the server.
        server_port (int): The port number of the server.
    """

    def __init__(self, server_ip, server_port):
        self.server_address = (server_ip, server_port)

    def send_command(self, command):
        """
        Sends a command to the server.

        Args:
            command (str): The command to send to the server.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            try:
                # Connect to the server
                client_socket.connect(self.server_address)

                # Send the command to the server
                client_socket.sendall(command.encode("UTF-8"))

                # Wait for a response from the server
                response = client_socket.recv(4096)
                print(f"Received: {response.decode()}")
            except OSError as e:
                print(f"Error communicating with server: {e}")
            except Exception as e:
                print(f"Unexpected error communicating with server: {e}")