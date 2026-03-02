import pytest
from unittest.mock import Mock

from src.Agents.Messages.Messages import (
    SystemMessage,
    UserMessage,
    ToolCall,
    ToolMessage,
    AIMessage
)
from src.Agents.Brain.ToolLLM import (
    MyClassesToLangchainParser,
    LangchainToMyClassesParser,
    ToolLLM
)


@pytest.fixture
def parameters():
    return {"x": 10, "y": 20}


@pytest.fixture
def tool_call(parameters):
    return ToolCall("add", parameters, "tool-1")


@pytest.fixture
def ai_message(tool_call):
    return AIMessage("hello", [tool_call])


@pytest.fixture
def my_to_lang_parser():
    return MyClassesToLangchainParser()


@pytest.fixture
def lang_to_my_parser():
    return LangchainToMyClassesParser()


class TestMyClassesToLangchainParser:
    def test_parse_system_message(self, my_to_lang_parser):
        msg = SystemMessage("system")
        parsed = my_to_lang_parser.parse_system_message(msg)

        assert parsed.content == "system"

    def test_parse_user_message(self, my_to_lang_parser):
        msg = UserMessage("user")
        parsed = my_to_lang_parser.parse_user_message(msg)

        assert parsed.content == "user"

    def test_parse_tool_message(self, my_to_lang_parser):
        msg = ToolMessage("result", "tool-1")
        parsed = my_to_lang_parser.parse_tool_message(msg)

        assert parsed.content == "result"
        assert parsed.tool_call_id == "tool-1"

    def test_parse_tool_call(self, my_to_lang_parser, tool_call, parameters):
        parsed = my_to_lang_parser.parse_tool_call(tool_call)

        assert parsed == {
            "name": "add",
            "args": parameters,
            "id": "tool-1",
        }

    def test_parse_ai_message(self, my_to_lang_parser, ai_message):
        parsed = my_to_lang_parser.parse_ai_message(ai_message)

        assert parsed.content == "hello"
        assert len(parsed.tool_calls) == 1
        assert parsed.tool_calls[0]["name"] == "add"


class TestLangchainToMyClassesParser:
    def test_parse_tool_call(self, lang_to_my_parser):
        langchain_tool_call = {
            "name": "add",
            "args": {"x": 10},
            "id": "tool-1",
        }

        parsed = lang_to_my_parser.parse_tool_call(langchain_tool_call)

        assert parsed.get_tool_name() == "add"
        assert parsed.get_parameters() == {"x": 10}
        assert parsed.get_id() == "tool-1"

    def test_parse_tool_message(self, lang_to_my_parser):
        langchain_tool_message = Mock()
        langchain_tool_message.content = "result"
        langchain_tool_message.tool_call_id = "tool-1"

        parsed = lang_to_my_parser.parse_tool_message(langchain_tool_message)

        assert parsed.get_content() == "result"
        assert parsed.get_id() == "tool-1"

    def test_parse_ai_message(self, lang_to_my_parser):
        langchain_tool_call = {"name": "add", "args": {}, "id": "tool-1"}

        langchain_ai_message = Mock()
        langchain_ai_message.content = "hello"
        langchain_ai_message.tool_calls = [langchain_tool_call]

        parsed = lang_to_my_parser.parse_ai_message(langchain_ai_message)

        assert parsed.get_content() == "hello"
        assert len(parsed.get_tool_calls()) == 1


class TestToolLLM:
    @pytest.fixture
    def llm(self):
        return Mock()

    @pytest.fixture
    def tool_llm(self, llm, my_to_lang_parser, lang_to_my_parser):
        return ToolLLM(llm, my_to_lang_parser, lang_to_my_parser)

    def test_bind_tools_with_empty_dict(self, tool_llm):
        tool_llm.bind_tools({})

        assert tool_llm.tool_llm is None
        assert tool_llm.tools == {}

    def test_bind_tools_with_tools(self, tool_llm, llm):
        mock_tool = Mock()
        llm.bind_tools.return_value = "BOUND_LLM"

        tool_llm.bind_tools({"add": mock_tool})

        assert tool_llm.tool_llm == "BOUND_LLM"
        llm.bind_tools.assert_called_once()

    def test_complete_chat_without_tools(self, tool_llm, llm):
        langchain_ai_message = Mock()
        langchain_ai_message.content = "response"
        langchain_ai_message.tool_calls = []

        llm.invoke.return_value = langchain_ai_message

        result = tool_llm.complete_chat([UserMessage("hello")])

        assert isinstance(result, AIMessage)
        assert result.get_content() == "response"

    def test_call_tool(self, tool_llm, tool_call):
        mock_langchain_tool_message = Mock()
        mock_langchain_tool_message.content = "tool result"
        mock_langchain_tool_message.tool_call_id = "tool-1"

        mock_tool = Mock()
        mock_tool.invoke.return_value = mock_langchain_tool_message

        tool_llm.tools = {"add": mock_tool}

        result = tool_llm.call_tool(tool_call)

        assert isinstance(result, ToolMessage)
        assert result.get_content() == "tool result"
        assert result.get_id() == "tool-1"
