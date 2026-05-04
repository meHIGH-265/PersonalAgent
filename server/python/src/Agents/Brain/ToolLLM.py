from langchain_core.messages import (
    AIMessage as LangchainAIMessage,
    BaseMessage as LangchainBaseMessage,
    HumanMessage as LangchainHumanMessage,
    SystemMessage as LangchainSystemMessage,
    ToolMessage as LangchainToolMessage
)
from langchain_core.messages.tool import ToolCall as LangchainToolCall
from langchain_core.tools import BaseTool, StructuredTool
from langchain_openai.chat_models.base import ChatOpenAI
from pydantic import BaseModel, create_model
from typing import Any, Callable

from src.Agents.Tools.Tool import Tool
from src.Agents.Messages.Messages import AIMessage, Message, SystemMessage, ToolCall, ToolMessage, UserMessage


class ToolLLM:
    class MyClassesToLangchainParser:
        """
        My Messages -> Langchain Messages
        """
        def __init__(self):
            pass

        @staticmethod
        def parse_system_message(system_message: SystemMessage) -> LangchainSystemMessage:
            return LangchainSystemMessage(system_message.get_content())

        @staticmethod
        def parse_user_message(user_message: UserMessage) -> LangchainHumanMessage:
            return LangchainHumanMessage(user_message.get_content())

        @staticmethod
        def parse_tool_message(tool_message: ToolMessage) -> LangchainToolMessage:
            content: str = tool_message.get_content()
            tool_call_id: str = tool_message.get_id()
            return LangchainToolMessage(content=content, tool_call_id=tool_call_id)

        @staticmethod
        def parse_tool_call(tool_call: ToolCall) -> LangchainToolCall:
            return {
                'name': tool_call.get_tool_name(),
                'args': tool_call.get_parameters(),
                'id': tool_call.get_id()
            }

        @staticmethod
        def parse_ai_message(ai_message: AIMessage) -> LangchainAIMessage:
            content: str = ai_message.get_content()
            tool_calls: list[LangchainToolCall] = [
                ToolLLM.MyClassesToLangchainParser.parse_tool_call(tool_call)
                for tool_call in ai_message.get_tool_calls()
            ]
            return LangchainAIMessage(content=content, tool_calls=tool_calls)

        @staticmethod
        def parse_message(
                message: Message | SystemMessage | UserMessage | ToolMessage | AIMessage
        ) -> LangchainBaseMessage | LangchainSystemMessage | LangchainHumanMessage | LangchainToolMessage | LangchainAIMessage:
            transformers: dict[type, Callable] = {
                SystemMessage: ToolLLM.MyClassesToLangchainParser.parse_system_message,
                UserMessage: ToolLLM.MyClassesToLangchainParser.parse_user_message,
                ToolMessage: ToolLLM.MyClassesToLangchainParser.parse_tool_message,
                AIMessage: ToolLLM.MyClassesToLangchainParser.parse_ai_message
            }
            try:
                return transformers[type(message)](message)
            except KeyError as _:
                raise ValueError(f'The type: "{type(message)}" could not be handeled.')

        @staticmethod
        def parse_tool(tool: Tool) -> BaseTool:
            def dict_to_model(name: str, fields: dict[str, type]) -> type[BaseModel]:
                return create_model(name, **{field_name: (field_type, ...) for field_name, field_type in fields.items()})

            def dummy_function(*args, **kwargs) -> Any:
                pass

            return StructuredTool(
                name=tool.get_name(),
                description=tool.get_description(),
                args_schema=dict_to_model(f'{tool.get_name()}Input', tool.get_args_schema()),
                func=dummy_function
            )

    class LangchainToMyClassesParser:
        """
        Langchain Messages -> My Messages
        """
        def __init__(self):
            pass

        @staticmethod
        def parse_tool_call(langchain_tool_call: LangchainToolCall) -> ToolCall:
            tool_name: str = langchain_tool_call.get('name')
            parameters: dict[str, Any] = langchain_tool_call.get('args')
            tool_call_id: str = langchain_tool_call.get('id')

            return ToolCall(tool_name, parameters, tool_call_id)

        @staticmethod
        def parse_ai_message(langchain_ai_message: LangchainAIMessage) -> AIMessage:
            content: str = langchain_ai_message.content
            tool_calls: list[ToolCall] = [
                ToolLLM.LangchainToMyClassesParser.parse_tool_call(tool_call)
                for tool_call in langchain_ai_message.tool_calls
            ]
            return AIMessage(content, tool_calls)

    def __init__(self, llm: ChatOpenAI, mine_to_lang_parser: MyClassesToLangchainParser,
                 lang_to_mine_parser: LangchainToMyClassesParser):
        self.llm: ChatOpenAI = llm
        self.tool_llm = None
        self.tools: dict[str, Tool] = {}
        self.mine_to_lang_parser: ToolLLM.MyClassesToLangchainParser = mine_to_lang_parser
        self.lang_to_mine_parser: ToolLLM.LangchainToMyClassesParser = lang_to_mine_parser

    def bind_tools(self, tools: dict[str, Tool]) -> None:
        if not tools:
            self.tool_llm = None
            self.tools.clear()
            return
        self.tools = tools
        langchain_tools: list[BaseTool] = [self.mine_to_lang_parser.parse_tool(tool) for tool in self.tools.values()]
        self.tool_llm = self.llm.bind_tools(langchain_tools)

    def add_tools(self, tools: dict[str, Tool]) -> None:
        tools |= self.tools
        self.bind_tools(tools)

    def complete_chat(self, message_list: list[Message | SystemMessage | UserMessage | AIMessage | ToolMessage]) -> AIMessage:
        langchain_message_list = [self.mine_to_lang_parser.parse_message(message) for message in message_list]
        langchain_ai_response: LangchainAIMessage = (self.tool_llm or self.llm).invoke(langchain_message_list)
        return self.lang_to_mine_parser.parse_ai_message(langchain_ai_response)
