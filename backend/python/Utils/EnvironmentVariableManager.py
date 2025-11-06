DEFAULT_CONSOLE_LOGGING: bool = False
DEFAULT_FILE_LOGGING: bool = False
DEFAULT_LOGGING_DIRECTORY_NAME: str = 'Logs'
DEFAULT_LOGGING_DIRECTORY: str = f'{f'{__file__}'.split('\\Utils')[0]}\\{DEFAULT_LOGGING_DIRECTORY_NAME}'
DEFAULT_LOG_FILE: str = 'log.txt'


def get_default_console_logging() -> bool:
    return DEFAULT_CONSOLE_LOGGING


def get_default_file_logging() -> bool:
    return DEFAULT_FILE_LOGGING


def get_default_logging_directory() -> str:
    return DEFAULT_LOGGING_DIRECTORY


def get_default_log_file() -> str:
    return DEFAULT_LOG_FILE


DEFAULT_HOST: str = '127.0.0.1'
DEFAULT_PORT: int = 5001
DEFAULT_TOOL_HOST: str = '127.0.0.1'
DEFAULT_TOOL_PORT: int = 7001


def get_default_host() -> str:
    return DEFAULT_HOST


def get_default_port() -> int:
    return DEFAULT_PORT


def get_default_tool_host() -> str:
    return DEFAULT_TOOL_HOST


def get_default_tool_port() -> int:
    return DEFAULT_TOOL_PORT


DEFAULT_AGENT_SYSTEM_PROMPT: str = 'You are a helpfull AI assistant.'
DEFAULT_AGENT_NAME: str = 'Agent'


def get_default_agent_system_prompt() -> str:
    return DEFAULT_AGENT_SYSTEM_PROMPT


def get_default_agent_name() -> str:
    return DEFAULT_AGENT_NAME


def main():
    print(f'{__file__} is running...')


if __name__ == '__main__':
    main()
