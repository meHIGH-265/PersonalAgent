from threading import Lock

from Utils.EnvironmentVariableManager import get_default_file_logging, get_default_console_logging, get_default_log_file


console_logging = get_default_console_logging()
console_lock = Lock()

file_logging = get_default_file_logging()
log_file = get_default_log_file()
file_lock = Lock()

separator = '-_' * 50 + '-'


def set_console_logging(_console_logging: bool | None = None) -> None:
    global console_logging
    if _console_logging is None:
        console_logging = get_default_console_logging()
    else:
        console_logging = _console_logging


def set_file_logging(_file_logging: bool | None = None) -> None:
    global file_logging
    if _file_logging is None:
        file_logging = get_default_file_logging()
    else:
        file_logging = _file_logging


def set_log_file(_log_file: str | None = None) -> None:
    global log_file
    if _log_file is None:
        log_file = get_default_log_file()
    else:
        log_file = _log_file


def log_console_now(x):
    if console_logging:
        with console_lock:
            print(x, flush=True)


def log_file_now(x):
    if file_logging:
        with file_lock:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f'{x}\n')


def log(x, use_separator=True):
    if use_separator:
        log_console_now(separator)
        log_file_now(separator)
    if x:
        log_console_now(x)
        log_file_now(x)


def main():
    print(f'{__file__} is running...')


if __name__ == '__main__':
    main()
