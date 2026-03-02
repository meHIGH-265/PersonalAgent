import pytest

from src.Agents.AgentLogic.AgentIDs import AgentIDs


class TestAgentIDsInitialization:
    def test_default_initialization(self):
        agent_ids = AgentIDs()

        assert agent_ids.Special == ["error", "stop", "supervisor", "user"]
        assert agent_ids.Workers == []
        assert agent_ids.All == agent_ids.Special

    def test_initialization_with_workers(self):
        agent_ids = AgentIDs(workers=["worker1", "worker2"])

        assert agent_ids.Workers == ["worker1", "worker2"]
        assert agent_ids.All == agent_ids.Special + ["worker1", "worker2"]


class TestAgentIDsAdd:
    def test_add_new_agent_id(self):
        agent_ids = AgentIDs()

        agent_ids.add("WorkerA")

        assert "workera" in agent_ids.Workers
        assert "workera" in agent_ids.All

    def test_add_does_not_duplicate_existing_id(self):
        agent_ids = AgentIDs(workers=["worker1"])

        agent_ids.add("worker1")

        assert agent_ids.Workers.count("worker1") == 1
        assert agent_ids.All.count("worker1") == 1

    def test_add_does_not_add_special_ids(self):
        agent_ids = AgentIDs()

        agent_ids.add("ERROR")

        assert "error" not in agent_ids.Workers
        assert agent_ids.All == agent_ids.Special
