from dotenv import load_dotenv
from langchain_openai.chat_models.base import ChatOpenAI
from os import getenv
from pydantic import SecretStr


class ChatOpenAIFactory:
    def __init__(self):
        load_dotenv()
        self.default_openai_api_key: str = getenv('OPENAI_API_KEY')
        self.default_model: str = getenv('OPENAI_MODEL')

    def create(self, openai_api_key: str | None = None, model: str | None = None) -> ChatOpenAI:
        openai_api_key: str = openai_api_key or self.default_openai_api_key
        model: str = model or self.default_model
        return ChatOpenAI(model=model, api_key=SecretStr(openai_api_key))
