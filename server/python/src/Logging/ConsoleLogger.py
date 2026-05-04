from threading import Lock
from typing import Any

from src.Logging.Logger import Logger


class ConsoleLogger(Logger):
    def __init__(self, separator: str = '-' * 100):
        super().__init__(separator)

        self.console_lock: Lock = Lock()

    def __log_console_now(self, content: str):
        with self.console_lock:
            print(content, end='', flush=True)

    def log(self, x: Any, who: str | None = None, use_separator: bool = True, use_timestamp: bool = True):
        content: str = self._generate_content(x, who, use_separator, use_timestamp)
        self.__log_console_now(content)
