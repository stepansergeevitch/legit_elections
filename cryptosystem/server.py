import socket
import threading
from datetime import timedelta, datetime

try:
    from .crypto import Crypto
except ImportError:
    class Crypto:

        def __init__(self, server):
            pass

        public_key = ("", "")

        def process(self, data):
            pass


bind_ip = '0.0.0.0'
bind_port = 9999


class Server:
    KEY_REQUEST = "KEY\n"
    DATA_REQUEST = "DATA\n"
    SUCCESS = "SUCCESS\n"
    ERROR = "ERROR\n"

    def __init__(self, ip_address="127.0.0.1", post=9999, backlog=5, max_seconds=5 * 60):
        self.crypto = Crypto(self)
        self.crypto = Crypto(self)
        self.stop_signal = threading.Event()
        self.backlog = backlog
        self.max_work_time = timedelta(seconds=max_seconds)

        self.bind_ip = ip_address
        self.bind_port = post
        self.main_thread = None
        self.iterations_count = 0
        self.listen_timeout = 1
        self.started = None

    def run(self):
        self.stop_signal.clear()
        self.main_thread = threading.Thread(target=self.serve_forever)
        self.main_thread.start()

    def serve_forever(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.bind_ip, self.bind_port))
        server.listen(self.backlog)
        server.settimeout(self.listen_timeout)
        print(f"Started listening on {self.bind_ip}:{self.bind_port}")

        self.started = datetime.now()
        time_exceeded = False
        while self._continue() and not time_exceeded:
            try:
                client_sock, address = server.accept()
            except socket.timeout:
                pass
            else:
                print(f"Accepted connection from {address[0]}:{address[1]}")
                # client_handler = threading.Thread(
                #     target=self.handle_client_connection,
                #     args=(client_sock,)
                # )
                # client_handler.start()
                self.handle_client_connection(client_sock)
            time_exceeded = self._time_exceeded()

        if time_exceeded:
            print(f"Server exceeded time limit")

    def _continue(self):
        return not self.stop_signal.is_set()

    def _time_exceeded(self):
        return datetime.now() - self.started > self.max_work_time

    def stop(self):
        if self.main_thread is not None:
            self.stop_signal.set()
            self.main_thread.join()
            self.main_thread = None
        else:
            print("Server is already stopped")

    def handle_client_connection(self, client_socket):
        request = client_socket.recv(1024)
        print(f"Received {len(request)} bytes")
        try:
            if not request.startswith(Server.KEY_REQUEST):
                client_socket.send(Server.ERROR)
            else:
                message = Server.KEY_REQUEST + '\n'.join(self.crypto.public_key)
                client_socket.send(message)

                request = client_socket.recv(1024)
                if not request.startswith(Server.DATA_REQUEST):
                    client_socket.send(Server.ERROR)
                else:
                    data = request[len(Server.DATA_REQUEST):]
                    self.crypto.process(data)
        except Exception as e:
            print(f"Server error: {e}")
            client_socket.send(Server.ERROR)
        else:
            print(f"Successful data transfer")
            client_socket.send(Server.SUCCESS)
        finally:
            client_socket.close()

    def wait_until_done(self):
        if self.main_thread is not None:
            self.main_thread.join()
