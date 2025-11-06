from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.tools import BaseTool
from langchain_openai.chat_models.base import ChatOpenAI
import os
from pydantic import SecretStr
from threading import Lock, Thread

# Load environment variables
load_dotenv()
default_openai_api_key = os.getenv('OPENAI_API_KEY')
default_model = os.getenv('OPENAI_MODEL')


class LlmSingletonClass:
    def __init__(self):
        self.llms: dict[str, dict[str, ChatOpenAI]] = {}
        self.lock = Lock()
        Thread(target=lambda: self.ensure_existance(), daemon=True).start()
        # This is called because creating a ChatOpenAI object takes a while
        # and running this in a separate thread makes the user's wait time shorter

    def ensure_existance(self, openai_api_key: str | None = None, model: str | None = None) -> bool:
        if not openai_api_key or not model:
            return False
        with self.lock:
            if openai_api_key in self.llms and model in self.llms[openai_api_key]:
                return True
            if openai_api_key not in self.llms:
                self.llms[openai_api_key] = {}
            if model not in self.llms[openai_api_key]:
                self.llms[openai_api_key][model] = ChatOpenAI(model=model, api_key=SecretStr(openai_api_key))
        return True

    def get_llm_instance(self, openai_api_key: str | None = None, model: str | None = None) -> ChatOpenAI | None:
        if not openai_api_key:
            openai_api_key = default_openai_api_key
        if not model:
            model = default_model
        if not self.ensure_existance(openai_api_key, model):
            return None
        return self.llms[openai_api_key][model]


LlmSingleton = LlmSingletonClass()


class LlmMock:
    @staticmethod
    def invoke(message_history: list[BaseMessage] | None = None) -> AIMessage:
        if not message_history:
            return AIMessage('Hello, how can I assist you today?')
        last_msg_content = message_history[-1].content
        response = f'Answer to: "{last_msg_content}"'
        return AIMessage(response)


class LLM:
    """
    Wrapper for the ChatOpenAI class provided by langchain
    """
    def __init__(self, llm: ChatOpenAI | type | None = None):
        self.llm = llm
        self.tools = {}
        self.tool_llm = None

    def bind_tools(self, tools: dict[str, BaseTool]) -> None:
        if not self.llm or type(self.llm) is type or not tools:
            self.tool_llm = None
            return
        self.tool_llm = self.llm.bind_tools(tools.values())
        self.tools = tools

    def invoke(self, message_history: list[BaseMessage] | None = None) -> AIMessage:
        if self.tool_llm:
            return self.tool_llm.invoke(message_history)
        if self.llm is None:
            return AIMessage('')
        return self.llm.invoke(message_history)


def get_llm_instance_with_tools(tools: dict[str, BaseTool] | None = None, openai_api_key: str | None = None, model: str | None = None, MOCK: bool = False) -> LLM:
    if MOCK:
        return LLM(LlmMock)
    if not tools:
        tools = {}
    chat_open_ai: ChatOpenAI | None = LlmSingleton.get_llm_instance(openai_api_key, model)
    llm = LLM(chat_open_ai)
    llm.bind_tools(tools)
    return llm


def main():
    print(f'{__file__} is running...')


if __name__ == '__main__':
    main()
