from threading import Lock
from typing import Any


from src.Logging.LogFileGenerator import LogFileGenerator, TimestampedLogFileGenerator


class Logger:
    def log(self, x: Any, who: str | None = None, use_separator: bool = True) -> None:
        pass


class ConsoleLogger(Logger):
    pass


class FileLogger(Logger):
    pass


class MixedLogger(Logger):
    @staticmethod
    def get_default_console_logging() -> bool:
        return True

    @staticmethod
    def get_default_file_logging() -> bool:
        return True

    def __init__(self, log_file_generator: LogFileGenerator, separator: str = '-' * 100):
        self.console_logging = self.get_default_console_logging()
        self.console_lock = Lock()

        self.default_log_file = log_file_generator.create_log_file()
        self.file_logging = self.get_default_file_logging()
        self.log_file = self.get_default_log_file()
        self.file_lock = Lock()

        self.separator = separator

    def set_console_logging(self, console_logging: bool | None = None) -> None:
        self.console_logging = console_logging
        if self.console_logging is None:
            self.console_logging = self.get_default_console_logging()

    def log_console_now(self, x: Any):
        if not self.console_logging:
            return

        with self.console_lock:
            print(x, flush=True)

    def get_default_log_file(self) -> str:
        return self.default_log_file

    def set_file_logging(self, file_logging: bool | None = None) -> None:
        self.file_logging = file_logging
        if self.file_logging is None:
            self.file_logging = self.get_default_file_logging()

    def set_log_file(self, log_file: str | None = None) -> None:
        self.log_file = log_file
        if not self.log_file:
            self.log_file = self.get_default_log_file()

    def log_file_now(self, x: Any):
        if not self.file_logging:
            return

        with self.file_lock:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f'{x}\n')

    def log(self, x: Any, who: str | None = None, use_separator: bool = True):
        if who:
            who = f'[ {who} ]: '
            x = f'{who}{f'{x}'.replace('\n', f'\n{' ' * len(who)}').replace('\t', '    ')}'

        if use_separator:
            self.log_console_now(self.separator)
            self.log_file_now(self.separator)
        if x:
            self.log_console_now(x)
            self.log_file_now(x)
