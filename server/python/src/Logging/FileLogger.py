from pathlib import Path
from threading import Lock
from typing import Any

from src.Logging.LogFileGenerator import LogFileGenerator
from src.Logging.Logger import Logger


class FileLogger(Logger):
    def __get_default_log_file(self) -> Path:
        return self.default_log_file

    def __init__(self, log_file_generator: LogFileGenerator, separator: str = '-' * 100):
        super().__init__(separator)

        self.default_log_file: Path = log_file_generator.create_log_file()
        self.log_file: Path = self.__get_default_log_file()
        self.file_lock: Lock = Lock()

    def set_log_file(self, log_file: Path | str | None = None) -> None:
        self.log_file = Path(log_file or self.__get_default_log_file())

    def __log_file_now(self, content: str):
        with self.file_lock:
            with self.log_file.open(mode='a', encoding='utf-8') as f:
                f.write(content)

    def log(self, x: Any, who: str | None = None, use_separator: bool = True, use_timestamp: bool = True):
        content: str = self._generate_content(x, who, use_separator, use_timestamp)
        self.__log_file_now(content)
