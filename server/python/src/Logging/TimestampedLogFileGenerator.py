from datetime import datetime
from pathlib import Path

from src.Logging.LogFileGenerator import LogFileGenerator


class TimestampedLogFileGenerator(LogFileGenerator):
    @staticmethod
    def get_default_logging_directory_path() -> Path:
        return Path(__file__).parents[2] / 'Logs'

    @staticmethod
    def get_default_log_file_name() -> str:
        return 'log.txt'

    def __init__(self, base_directory_path: Path | str | None = None, file_name: str | None = None):
        self.base_directory_path: Path = Path(base_directory_path or self.get_default_logging_directory_path())
        self.file_name: str = file_name or self.get_default_log_file_name()
        self.timestamp: datetime = datetime.now()

    def set_base_directory_path(self, base_directory_path: str | None = None) -> None:
        self.base_directory_path = Path(base_directory_path or self.get_default_logging_directory_path())

    def refresh_timestamp(self):
        self.timestamp = datetime.now()

    def get_timestamp(self) -> datetime:
        return self.timestamp

    def generate_nested_timestamped_directory_path(self, base_directory_path: Path | str | None = None) -> Path:
        base_directory_path = Path(base_directory_path or self.base_directory_path)

        now: datetime = self.get_timestamp()
        year: str = f'{now.year:04d}'
        month: str = f'{now.month:02d}'
        day: str = f'{now.day:02d}'
        hour_minute: str = f'{now.hour:02d}_{now.minute:02d}'

        return base_directory_path / year / month / day / hour_minute

    def create_nested_timestamped_log_file(self, base_directory_path: Path | str | None = None, file_name: str | None = None) -> Path:
        base_directory_path = Path(base_directory_path or self.base_directory_path)
        file_name = file_name or self.file_name

        timestamped_directory_path: Path = self.generate_nested_timestamped_directory_path(base_directory_path)
        timestamped_directory_path.mkdir(parents=True, exist_ok=True)
        timestamped_log_file_path: Path = timestamped_directory_path / file_name

        timestamped_log_file_path.touch(exist_ok=True)

        return timestamped_log_file_path

    def create_log_file(self) -> Path:
        return self.create_nested_timestamped_log_file()
