from requests import Response, post
from typing import Any

from src.Agents.Messages.Messages import ToolCall, ToolMessage
from src.Agents.Tools.ToolExecutor import ToolExecutor
from src.Logging.Logger import Logger


class RemoteToolExecutor(ToolExecutor):
    @staticmethod
    def get_default_tool_host() -> str:
        return '127.0.0.1'

    @staticmethod
    def get_default_tool_port() -> int:
        return 7001

    def __init__(self, logger: Logger, host: str | None = None, port: int | None = None):
        super().__init__(logger)

        self.host: str = host or RemoteToolExecutor.get_default_tool_host()
        self.port: int = port or RemoteToolExecutor.get_default_tool_port()

    def get_tool_host(self) -> str:
        return self.host

    def set_tool_host(self, host: str | None = None) -> None:
        self.host = host or RemoteToolExecutor.get_default_tool_host()

    def get_tool_port(self) -> int:
        return self.port

    def set_tool_port(self, port: int | None = None) -> None:
        self.port = port or RemoteToolExecutor.get_default_tool_port()

    def call_tool(self, tool_call: ToolCall) -> ToolMessage:
        """
            Sends a post request to the tool endpoint
            and logs this tool usage
        """
        self.log_tool_call(tool_call)

        url: str = f'http://{self.get_tool_host()}:{self.get_tool_port()}/call_tool'
        json_data: dict[str, Any] = tool_call.get_parameters() | {'tool_name': tool_call.get_tool_name()}
        headers: dict[str, str] = {'Content-Type': 'application/json'}

        try:
            response: Response = post(url=url, json=json_data, headers=headers)
            content: str = response.text
        except Exception as e:
            content: str = f'Tool calling endpoint is offline:\n{e}'

        return ToolMessage(content=content, tool_call_id=tool_call.get_id())
