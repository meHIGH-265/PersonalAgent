import pytest
from unittest.mock import patch

from src.Agents.Brain.ChatOpenAIFactory import ChatOpenAIFactory


class TestChatOpenAIFactory:
    @patch("src.Agents.Brain.ChatOpenAIFactory.ChatOpenAI")
    def test_create_uses_provided_api_key_and_model(self, mock_chat_openai):
        ChatOpenAIFactory.create(
            openai_api_key="test-key",
            model="gpt-test",
        )

        mock_chat_openai.assert_called_once()
        _, kwargs = mock_chat_openai.call_args

        assert kwargs["model"] == "gpt-test"
        assert kwargs["api_key"].get_secret_value() == "test-key"

    @patch("src.Agents.Brain.ChatOpenAIFactory.ChatOpenAI")
    @patch("src.Agents.Brain.ChatOpenAIFactory.default_openai_api_key", "env-key")
    @patch("src.Agents.Brain.ChatOpenAIFactory.default_model", "env-model")
    def test_create_falls_back_to_env_defaults(self, mock_chat_openai):
        ChatOpenAIFactory.create()

        mock_chat_openai.assert_called_once()
        _, kwargs = mock_chat_openai.call_args

        assert kwargs["model"] == "env-model"
        assert kwargs["api_key"].get_secret_value() == "env-key"
