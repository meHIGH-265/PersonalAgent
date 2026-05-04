from src.Agents.Messages.Messages import ToolCall, ToolMessage
from src.Logging.Logger import Logger


class ToolExecutor:
    def __init__(self, logger: Logger):
        self.logger: Logger = logger

    def log_tool_call(self, tool_call: ToolCall) -> None:
        log_string = f'The {tool_call.get_tool_name()} tool has been called with parameters:'
        for parameter_name, parameter in tool_call.get_parameters().items():
            if '\n' in parameter:
                log_string += f'\n{parameter_name}:\n\n{parameter}\n'
            else:
                log_string += f'\n{parameter_name}: {parameter}'
        self.logger.log(log_string, who='TOOLS', use_separator=True, use_timestamp=True)

    def call_tool(self, tool_call: ToolCall) -> ToolMessage:
        pass
