from queue import Queue, ShutDown
from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread


class Streamer:
    def __init__(self):
        self.queue: Queue = Queue()

    def start_streaming(self, host: str, port: int) -> None:
        def stream() -> None:
            with socket(AF_INET, SOCK_STREAM) as s:
                s.connect((host, port))

                while True:
                    try:
                        data: str = self.queue.get()
                    except ShutDown:
                        break
                    s.sendall(data.encode())

        Thread(target=stream, daemon=True).start()

    def send_data(self, data: str):
        self.queue.put(data)

    def stop_streaming(self):
        self.queue.shutdown()
