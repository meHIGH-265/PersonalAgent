from langchain_core.messages import (
    BaseMessage as LangchainBaseMessage,
    SystemMessage as LangchainSystemMessage,
    HumanMessage as LangchainHumanMessage,
    ToolMessage as LangchainToolMessage,
    AIMessage as LangchainAIMessage
)
from langchain_core.messages.tool import ToolCall as LangchainToolCall
from langchain_core.tools import BaseTool, StructuredTool
from langchain_openai.chat_models.base import ChatOpenAI
from pydantic import BaseModel, create_model
from typing import Any

from src.Agents.Tools.Tool import Tool
from src.Agents.Messages.Messages import Message, SystemMessage, UserMessage, ToolCall, ToolMessage, AIMessage


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
            content = tool_message.get_content()
            tool_call_id = tool_message.get_id()
            return LangchainToolMessage(content=content, tool_call_id=tool_call_id)

        @staticmethod
        def parse_tool_call(tool_call: ToolCall) -> LangchainToolCall:
            return {
                'name': tool_call.get_tool_name(),
                'args': tool_call.get_parameters(),
                'id': tool_call.get_id()
            }

        def parse_ai_message(self, ai_message: AIMessage) -> LangchainAIMessage:
            content = ai_message.get_content()
            tool_calls = [self.parse_tool_call(tc) for tc in ai_message.get_tool_calls()]
            return LangchainAIMessage(content=content, tool_calls=tool_calls)

        def parse_message(
                self,
                message: Message | SystemMessage | UserMessage | ToolMessage | AIMessage
        ) -> LangchainBaseMessage | LangchainSystemMessage | LangchainHumanMessage | LangchainToolMessage | LangchainAIMessage:
            transformers = {
                SystemMessage: self.parse_system_message,
                UserMessage: self.parse_user_message,
                ToolMessage: self.parse_tool_message,
                AIMessage: self.parse_ai_message
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
            tool_name = langchain_tool_call.get('name')
            parameters = langchain_tool_call.get('args')
            tool_call_id = langchain_tool_call.get('id')

            return ToolCall(tool_name, parameters, tool_call_id)

        @staticmethod
        def parse_tool_message(langchain_tool_message: LangchainToolMessage) -> ToolMessage:
            content = langchain_tool_message.content
            tool_call_id = langchain_tool_message.tool_call_id
            return ToolMessage(content, tool_call_id)

        def parse_ai_message(self, langchain_ai_message: LangchainAIMessage) -> AIMessage:
            content = langchain_ai_message.content
            tool_calls = [self.parse_tool_call(tool_call) for tool_call in langchain_ai_message.tool_calls]
            return AIMessage(content, tool_calls)

    def __init__(self, llm: ChatOpenAI, mine_to_lang_parser: MyClassesToLangchainParser,
                 lang_to_mine_parser: LangchainToMyClassesParser):
        self.llm = llm
        self.tool_llm = None
        self.tools: dict[str, Tool] = {}
        self.mine_to_lang_parser = mine_to_lang_parser
        self.lang_to_mine_parser = lang_to_mine_parser

    def bind_tools(self, tools: dict[str, Tool]):
        if not tools:
            self.tool_llm = None
            self.tools: dict[str, Tool] = {}
            return
        self.tools = tools
        langchain_tools = [self.mine_to_lang_parser.parse_tool(tool) for tool in self.tools.values()]
        self.tool_llm = self.llm.bind_tools(langchain_tools)

    def complete_chat(self, message_list: list[Message | SystemMessage | UserMessage | AIMessage | ToolMessage]) -> AIMessage:
        langchain_message_list = [self.mine_to_lang_parser.parse_message(message) for message in message_list]
        langchain_ai_response: LangchainAIMessage = self.tool_llm.invoke(
            langchain_message_list) if self.tool_llm else self.llm.invoke(langchain_message_list)
        return self.lang_to_mine_parser.parse_ai_message(langchain_ai_response)
