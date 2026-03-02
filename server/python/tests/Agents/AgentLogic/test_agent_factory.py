from unittest.mock import Mock

from src.Agents.AgentManager import MyAgentFactory


class TestAgentTemplates:
    def setup_method(self):
        MyAgentFactory.agent_templates.clear()

    def test_add_agent_template_registers_template(self):
        template = Mock()

        MyAgentFactory.add_agent_template("TestAgent", template)

        assert "testagent" in MyAgentFactory.agent_templates
        assert MyAgentFactory.agent_templates["testagent"] is template

    def test_create_new_agent_with_known_id(self):
        agent = Mock()
        template = Mock(return_value=agent)

        MyAgentFactory.add_agent_template("worker", template)

        result = MyAgentFactory.create_new_agent("worker")

        assert result is agent
        template.assert_called_once()

    def test_create_new_agent_with_unknown_id_returns_default(self, monkeypatch):
        default_agent = Mock()
        monkeypatch.setattr(MyAgentFactory, "default_template", lambda: default_agent)

        result = MyAgentFactory.create_new_agent("unknown")

        assert result is default_agent

    def test_create_new_agent_without_id_returns_default(self, monkeypatch):
        default_agent = Mock()
        monkeypatch.setattr(MyAgentFactory, "default_template", lambda: default_agent)

        result = MyAgentFactory.create_new_agent()

        assert result is default_agent
