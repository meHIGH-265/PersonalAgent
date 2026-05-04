from typing import Any


class Identifiable:
    def __init__(self, ID: str | None = None):
        self.ID: str | None = ID

    def get_id(self) -> str | None:
        return self.ID


class Message(Identifiable):
    def __init__(self, content: str, ID: str | None = None):
        super().__init__(ID)

        self.content: str = content

    def get_content(self) -> str:
        return self.content


class SystemMessage(Message):
    def __init__(self, content: str):
        super().__init__(content)


class UserMessage(Message):
    def __init__(self, content: str):
        super().__init__(content)


class ToolCall(Identifiable):
    def __init__(self, tool_name: str, parameters: dict[str, Any], tool_call_id: str):
        super().__init__(tool_call_id)

        self.tool_name: str = tool_name
        self.parameters: dict[str, Any] = parameters

    def get_tool_name(self) -> str:
        return self.tool_name

    def get_parameters(self) -> dict[str, Any]:
        return {k: v for k, v in self.parameters.items()}

    def get_parameter(self, parameter_name: str) -> Any:
        return self.parameters.get(parameter_name)


class ToolMessage(Message):
    def __init__(self, content: str, tool_call_id: str):
        super().__init__(content, tool_call_id)


class AIMessage(Message):
    def __init__(self, content: str, tool_calls: list[ToolCall] | None = None):
        super().__init__(content)

        self.tool_calls: list[ToolCall] = tool_calls if tool_calls else []

    def get_tool_calls(self) -> list[ToolCall]:
        return self.tool_calls

    def is_final(self) -> bool:
        return not self.get_tool_calls()

    def is_partial(self) -> bool:
        return not self.is_final()
