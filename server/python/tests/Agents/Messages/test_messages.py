import pytest

from src.Agents.Messages.Messages import (
    Identifiable,
    Message,
    SystemMessage,
    UserMessage,
    ToolCall,
    ToolMessage,
    AIMessage
)


class TestIdentifiable:
    def test_get_id_returns_id(self):
        obj = Identifiable("123")
        assert obj.get_id() == "123"

    def test_get_id_returns_none_when_missing(self):
        obj = Identifiable()
        assert obj.get_id() is None


class TestMessage:
    def test_content_and_id_are_set(self):
        msg = Message("hello", "msg-1")
        assert msg.get_content() == "hello"
        assert msg.get_id() == "msg-1"


class TestSystemMessage:
    def test_inherits_message_behavior(self):
        msg = SystemMessage("system")
        assert msg.get_content() == "system"
        assert msg.get_id() is None


class TestUserMessage:
    def test_inherits_message_behavior(self):
        msg = UserMessage("user")
        assert msg.get_content() == "user"
        assert msg.get_id() is None


@pytest.fixture
def x_y_parameters():
    return {"x": 10, "y": 20}


@pytest.fixture
def add_tool_call(x_y_parameters):
    return ToolCall(
        tool_name="add",
        parameters=x_y_parameters,
        tool_call_id="tool-1",
    )


class TestToolCall:
    def test_tool_call_stores_name_parameters_and_id(self, add_tool_call, x_y_parameters):
        assert add_tool_call.get_id() == "tool-1"
        assert add_tool_call.get_tool_name() == "add"
        assert add_tool_call.get_parameters() == x_y_parameters

    def test_get_parameter_returns_value(self, add_tool_call):
        assert add_tool_call.get_parameter("x") == 10
        assert add_tool_call.get_parameter("y") == 20

    def test_get_parameter_returns_none_if_missing(self, add_tool_call):
        assert add_tool_call.get_parameter("missing") is None



class TestToolMessage:
    def test_tool_message_sets_content_and_tool_call_id(self):
        msg = ToolMessage("result", "tool-1")
        assert msg.get_content() == "result"
        assert msg.get_id() == "tool-1"


class TestAIMessage:
    def test_initializes_without_tool_calls(self):
        msg = AIMessage("hello")

        assert msg.get_content() == "hello"
        assert msg.get_tool_calls() == []

    def test_initializes_with_tool_calls(self):
        call = ToolCall("echo", {"text": "hi"}, "tool-2")
        msg = AIMessage("hello", [call])

        assert len(msg.get_tool_calls()) == 1
        assert msg.get_tool_calls()[0].get_tool_name() == "echo"
