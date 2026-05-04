from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any

from src.Logging.LogFileGenerator import LogFileGenerator


class Logger:
    def __init__(self, separator: str = '-' * 100, tab_size: int = 4):
        self.separator: str = separator
        if tab_size < 0:
            tab_size = 0
        if tab_size > 16:
            tab_size = 16
        self.tab: str = ' ' * tab_size

    def _generate_content(self, x: Any, who: str | None = None, use_separator: bool = True, use_timestamp: bool = True) -> str:
        if who:
            who = f'[ {who} ]: '
            x = f'{who}{f'{x}'.replace('\n', f'\n{' ' * len(who)}').replace('\t', self.tab)}'

        content: str = f'{self.separator}\n' if use_separator else ''
        if use_timestamp:
            content += f'{datetime.now()}\n\n'
        if x:
            content += f'{x}\n\n'

        return content

    def log(self, x: Any, who: str | None = None, use_separator: bool = True, use_timestamp: bool = True) -> None:
        pass


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


class MixedLogger(Logger):
    @staticmethod
    def __get_default_console_logging() -> bool:
        return True

    @staticmethod
    def __get_default_file_logging() -> bool:
        return True

    def __get_default_log_file(self) -> Path:
        return self.default_log_file

    def __init__(self, log_file_generator: LogFileGenerator, separator: str = '-' * 100):
        super().__init__(separator)

        self.console_logging: bool = MixedLogger.__get_default_console_logging()
        self.console_lock: Lock = Lock()

        self.default_log_file: Path = log_file_generator.create_log_file()
        self.file_logging: bool = MixedLogger.__get_default_file_logging()
        self.log_file: Path = self.__get_default_log_file()
        self.file_lock: Lock = Lock()

    def set_console_logging(self, console_logging: bool | None = None) -> None:
        if console_logging is None:
            self.console_logging = self.__get_default_console_logging()
            return
        self.console_logging = console_logging

    def set_file_logging(self, file_logging: bool | None = None) -> None:
        if file_logging is None:
            self.file_logging = self.__get_default_file_logging()
            return
        self.file_logging = file_logging

    def set_log_file(self, log_file: Path | str | None = None) -> None:
        self.log_file = Path(log_file or self.__get_default_log_file())

    def __log_console_now(self, content: str):
        if not self.console_logging:
            return

        with self.console_lock:
            print(content, end='', flush=True)

    def __log_file_now(self, content: str):
        if not self.file_logging:
            return

        with self.file_lock:
            with self.log_file.open(mode='a', encoding='utf-8') as f:
                f.write(content)

    def log(self, x: Any, who: str | None = None, use_separator: bool = True, use_timestamp: bool = True):
        content: str = self._generate_content(x, who, use_separator, use_timestamp)
        self.__log_file_now(content)
        self.__log_console_now(content)
