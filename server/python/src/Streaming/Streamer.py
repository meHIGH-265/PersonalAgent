import queue
import socket
from threading import Thread


class Streamer:
    def __init__(self):
        self.queue = queue.Queue()

    def start_streaming(self, host: str, port: int) -> None:
        def stream() -> None:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))

                while True:
                    data = self.queue.get()
                    if data is None:
                        break
                    s.sendall(data.encode())

        Thread(target=stream, daemon=True).start()

    def send_data(self, data: str):
        self.queue.put(data)

    def stop_streaming(self):
        self.queue.put(None)
