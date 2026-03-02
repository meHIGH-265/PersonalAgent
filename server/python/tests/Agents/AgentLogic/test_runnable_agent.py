import pytest
from typing import cast
from unittest.mock import Mock

from src.Agents.Agent import (
    Agent
)
from src.Agents.Messages.Messages import (
    SystemMessage,
    UserMessage,
    AIMessage
)


@pytest.fixture
def mock_llm():
    return Mock()


@pytest.fixture
def agent(mock_llm):
    return Agent(llm=mock_llm)


class TestRunnableAgentInitialization:
    def test_defaults_are_set(self, agent):
        assert agent.name == Agent.get_default_agent_name()
        assert agent.description == ""
        assert isinstance(agent.instructions, SystemMessage)
        assert agent.instructions.get_content() == Agent.get_default_agent_system_prompt()

    def test_message_history_starts_with_system_message(self, agent):
        assert len(agent.message_history) == 1
        assert isinstance(agent.message_history[0], SystemMessage)


class TestRunnableAgentWorkingState:
    def test_initially_not_working(self, agent):
        assert agent.is_working() is False

    def test_set_working_state(self, agent):
        agent.set_working_state(True)
        assert agent.is_working() is True

        agent.set_working_state(False)
        assert agent.is_working() is False


class TestRunnableAgentTasks:
    def test_add_task(self, agent):
        submit = Mock()
        agent.add_task("do something", submit)

        task, callback = agent.get_next_task()
        assert task == "do something"
        assert callback is submit

    def test_add_empty_task_is_ignored(self, agent):
        submit = Mock()
        agent.add_task("", submit)

        task, _ = agent.get_next_task()
        assert task is None

    def test_get_next_task_when_empty(self, agent):
        task, callback = agent.get_next_task()
        assert task is None
        assert callable(callback)


class TestRunnableAgentCompleteChat:
    def test_complete_chat_appends_ai_message(self, agent, mock_llm):
        ai_message = AIMessage("hello")
        mock_llm.complete_chat.return_value = ai_message

        result = agent.complete_chat()

        assert result is ai_message
        assert agent.message_history[-1] is ai_message
        mock_llm.complete_chat.assert_called_once()

    def test_complete_chat_raises_should_pause(self, agent):
        with agent.working_state_lock:
            agent.should_pause = True

        with pytest.raises(Agent.ShouldPause):
            agent.complete_chat()


class TestRunnableAgentToolLoop:
    def test_returns_immediately_if_no_tool_calls(self, agent, mock_llm):
        ai_message = AIMessage("final")
        mock_llm.complete_chat.return_value = ai_message

        result = agent.complete_chat_until_no_tools_are_called()

        assert result is ai_message
        assert agent.message_history[-1] is ai_message

    def test_processes_tool_calls_until_done(self, agent, mock_llm):
        tool_call = Mock()
        tool_call.get_tool_calls = Mock(return_value=[])

        ai_with_tool = AIMessage("needs tool", tool_calls=[tool_call])
        ai_final = AIMessage("done")

        mock_llm.complete_chat.side_effect = [ai_with_tool, ai_final]
        mock_llm.call_tool.return_value = Mock()

        result = agent.complete_chat_until_no_tools_are_called()

        assert result.get_content() == "done"
        assert mock_llm.call_tool.called


class TestRunnableAgentResume:
    def test_no_action_if_last_message_is_system(self, agent):
        agent.resume_last_task_if_not_complete()
        assert len(agent.message_history) == 1

    def test_no_action_if_last_ai_message_has_no_tool_calls(self, agent):
        agent.message_history.append(AIMessage("done"))
        agent.resume_last_task_if_not_complete()

        assert agent.message_history[-1].get_content() == "done"

    def test_resumes_if_last_ai_message_has_tool_calls(self, agent, mock_llm):
        tool_call = Mock()
        tool_call.get_tool_calls = Mock(return_value=[])

        ai_with_tool = AIMessage("needs tool", tool_calls=[tool_call])
        ai_final = AIMessage("done")

        agent.message_history.append(ai_with_tool)
        agent.submit_answer = Mock()

        mock_llm.complete_chat.side_effect = [ai_final]
        mock_llm.call_tool.return_value = Mock()

        agent.resume_last_task_if_not_complete()

        cast(Mock, agent.submit_answer).assert_called_once_with("done")


class TestRunnableAgentSolveTask:
    def test_solve_task_appends_user_message_and_returns_answer(self, agent, mock_llm):
        ai_message = AIMessage("answer")
        mock_llm.complete_chat.return_value = ai_message

        result = agent.solve_task("what is this?")

        assert result == "answer"
        assert isinstance(agent.message_history[-2], UserMessage)
        assert agent.message_history[-1] is ai_message


class TestRunnableAgentPublicAPI:
    def test_give_task_adds_task(self, agent):
        submit = Mock()
        agent.set_working_state(True)
        agent.give_task("task", submit)
        agent.set_working_state(False)

        task, _ = agent.get_next_task()
        assert task == "task"

    def test_pause_work_sets_flag(self, agent):
        agent.set_working_state(True)
        agent.pause_work()

        with agent.working_state_lock:
            assert agent.should_pause is True

    def test_clear_history_resets_state(self, agent):
        submit = Mock()
        agent.add_task("task", submit)
        agent.message_history.append(UserMessage("hi"))

        agent.clear_history()

        assert len(agent.message_history) == 1
        assert isinstance(agent.message_history[0], SystemMessage)
        assert agent.tasks == []
