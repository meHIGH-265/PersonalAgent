from datetime import datetime
import os


class LogFileGenerator:
    def create_log_file(self):
        pass


class TimestampedLogFileGenerator(LogFileGenerator):
    @staticmethod
    def get_default_logging_directory_path() -> str:
        return f'{f'{__file__}'.split('\\src\\Logging\\')[0]}\\Logs'

    @staticmethod
    def get_default_log_file_name() -> str:
        return 'log.txt'

    def __init__(self, base_directory_path: str | None = None, file_name: str | None = None):
        self.base_directory_path = base_directory_path
        if self.base_directory_path is None:
            self.base_directory_path = self.get_default_logging_directory_path()
        self.file_name = file_name
        if self.file_name is None:
            self.file_name = self.get_default_log_file_name()
        self.timestamp = datetime.now()

    def set_base_directory_path(self, base_directory_path: str | None = None) -> None:
        self.base_directory_path = base_directory_path
        if not self.base_directory_path:
            self.base_directory_path = self.get_default_logging_directory_path()

    def refresh_timestamp(self):
        self.timestamp = datetime.now()

    def get_timestamp(self):
        return self.timestamp

    def generate_nested_timestamped_directory_path(self, base_directory_path: str | None = None) -> str:
        if not base_directory_path:
            base_directory_path = self.base_directory_path

        now = self.get_timestamp()
        year = f'{now.year:04d}'
        month = f'{now.month:02d}'
        day = f'{now.day:02d}'
        hour_minute = f'{now.hour:02d}_{now.minute:02d}'

        full_path = os.path.join(base_directory_path, year, month, day, hour_minute)

        return full_path

    def create_nested_timestamped_log_file(self, base_directory_path: str | None = None, file_name: str | None = None) -> str:
        if not base_directory_path:
            base_directory_path = self.base_directory_path
        if not file_name:
            file_name = self.file_name

        timestamped_directory_path = self.generate_nested_timestamped_directory_path(base_directory_path)
        os.makedirs(timestamped_directory_path, exist_ok=True)
        timestamped_log_file_path = os.path.join(timestamped_directory_path, file_name)

        if not os.path.exists(timestamped_log_file_path):
            try:
                with open(timestamped_log_file_path, 'w', encoding='utf-8') as file:
                    file.write('')
            except OSError as _:
                pass

        return timestamped_log_file_path

    def create_log_file(self) -> str:
        return self.create_nested_timestamped_log_file()
