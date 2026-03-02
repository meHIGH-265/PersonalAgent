from dotenv import load_dotenv
from langchain_openai.chat_models.base import ChatOpenAI
import os
from pydantic import SecretStr


load_dotenv()
default_openai_api_key = os.getenv('OPENAI_API_KEY')
default_model = os.getenv('OPENAI_MODEL')


class ChatOpenAIFactory:
    def __init__(self):
        pass

    @staticmethod
    def create(openai_api_key: str | None = None, model: str | None = None) -> ChatOpenAI:
        if not openai_api_key:
            openai_api_key = default_openai_api_key
        if not model:
            model = default_model
        return ChatOpenAI(model=model, api_key=SecretStr(openai_api_key))
