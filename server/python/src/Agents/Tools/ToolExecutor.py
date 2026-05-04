import requests

from src.Agents.Messages.Messages import ToolCall, ToolMessage
from src.Logging.Logger import Logger


class ToolExecutor:
    def call_tool(self, tool_call: ToolCall) -> ToolMessage:
        pass


class RemoteToolExecutor(ToolExecutor):
    @staticmethod
    def get_default_tool_host() -> str:
        return '127.0.0.1'

    @staticmethod
    def get_default_tool_port() -> int:
        return 7001

    def __init__(self, logger: Logger, host: str | None = None, port: int | None = None):
        self.logger = logger
        self.host, self.port = None, None
        self.set_tool_host(host)
        self.set_tool_port(port)

    def get_tool_host(self) -> str:
        return self.host

    def set_tool_host(self, host: str | None = None) -> None:
        if host is None:
            self.host = self.get_default_tool_host()
        else:
            self.host = host

    def get_tool_port(self) -> int:
        return self.port

    def set_tool_port(self, port: int | None = None) -> None:
        if port is None:
            self.port = self.get_default_tool_port()
        else:
            self.port = port

    def call_tool(self, tool_call: ToolCall) -> ToolMessage:
        """
            Sends a post request to the tool endpoint
            and logs this tool usage
        """
        tool_name = tool_call.get_tool_name()
        json_data = tool_call.get_parameters()

        def log_tool_call() -> None:
            log_string = f'The {tool_name} tool has been called with parameters:'
            for parameter_name, parameter in json_data.items():
                if '\n' in parameter:
                    log_string += f'\n{parameter_name}:\n\n{parameter}\n'
                else:
                    log_string += f'\n{parameter_name}: {parameter}'
            self.logger.log(log_string, who='TOOLS', use_separator=True)

        log_tool_call()

        url = f'http://{self.get_tool_host()}:{self.get_tool_port()}/call_tool'
        json_data['tool_name'] = tool_name
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(url=url, json=json_data, headers=headers)
            content = response.text
        except Exception as e:
            content = f'An error occoured while trying to run the tool on the user\'s machine:\n{e}'

        return ToolMessage(content=content, tool_call_id=tool_call.get_id())
