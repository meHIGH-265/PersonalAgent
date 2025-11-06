from datetime import datetime
import os

from Utils.EnvironmentVariableManager import get_default_logging_directory, get_default_log_file

DEFAULT_BASE_PATH = get_default_logging_directory()
BASE_PATH = DEFAULT_BASE_PATH
DEFAULT_LOGGING_FILE = get_default_log_file()
TIMESTAMP = datetime.now()


def set_base_path(base_path: str | None = None) -> None:
    global BASE_PATH
    if base_path is None:
        BASE_PATH = DEFAULT_BASE_PATH
    else:
        BASE_PATH = base_path


def refresh_timestamp():
    global TIMESTAMP
    TIMESTAMP = datetime.now()


def get_timestamp():
    return TIMESTAMP


def generate_nested_timestamped_directory_path(base_path: str | None = None) -> str:
    if base_path is None:
        base_path = BASE_PATH

    now = get_timestamp()
    year = f'{now.year:04d}'
    month = f'{now.month:02d}'
    day = f'{now.day:02d}'
    hour_minute = f'{now.hour:02d}_{now.minute:02d}'

    full_path = os.path.join(base_path, year, month, day, hour_minute)

    return full_path


def create_nested_timestamped_log_file(log_file: str | None = None) -> str:
    if log_file is None:
        log_file = DEFAULT_LOGGING_FILE

    log_file_dir_path = generate_nested_timestamped_directory_path(BASE_PATH)
    os.makedirs(log_file_dir_path, exist_ok=True)
    log_file_path = os.path.join(log_file_dir_path, log_file)

    if not os.path.exists(log_file_path):
        try:
            with open(log_file_path, 'w', encoding='utf-8') as file:
                file.write('')
        except OSError as _:
            pass

    return log_file_path


def main():
    print(f'{__file__} is running...')


if __name__ == '__main__':
    main()
