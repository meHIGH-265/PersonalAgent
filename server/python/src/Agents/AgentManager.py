import json
from pathlib import Path
from typing import Any

from src.Agents.Agent import Agent
from src.Agents.Brain.ChatOpenAIFactory import ChatOpenAIFactory
from src.Agents.Brain.ToolLLM import ToolLLM
from src.Agents.Tools.ToolExecutor import ToolExecutor
from src.Agents.Tools.ToolManager import ToolManager
from src.Logging.CustomLogging import Logger


class AgentManager:
    @staticmethod
    def load_all_agent_details(agent_folder: Path) -> list[dict]:
        agent_details = []

        for json_file in agent_folder.glob('*.json'):
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                agent_details.append(data)

        return agent_details

    @staticmethod
    def get_default_llm_instance() -> ToolLLM:
        return ToolLLM(
            ChatOpenAIFactory.create(),
            ToolLLM.MyClassesToLangchainParser(),
            ToolLLM.LangchainToMyClassesParser()
        )

    def get_fully_tooled_llm_instance(self) -> ToolLLM:
        llm = ToolLLM(
            ChatOpenAIFactory.create(),
            ToolLLM.MyClassesToLangchainParser(),
            ToolLLM.LangchainToMyClassesParser()
        )
        llm.bind_tools(self.tool_manager.get_tools_by_name())
        return llm

    def convert_agent_details_to_agent(self, agent_details: dict[str, Any]) -> Agent:
        name = agent_details['name']
        description = agent_details['description']
        instructions = agent_details['instructions']
        tool_names = agent_details['tool_names']

        llm = self.get_default_llm_instance()
        tools = self.tool_manager.get_tools_by_name(tool_names)
        llm.bind_tools(tools)

        logger = self.logger
        tool_executor = self.tool_executor

        return Agent(llm, logger, tool_executor, name, description, instructions)

    def __init__(self, logger: Logger, tool_executor: ToolExecutor, tool_manager: ToolManager, agent_folder: str | None = None):
        self.logger = logger
        self.tool_executor = tool_executor
        self.tool_manager = tool_manager

        if agent_folder is None:
            self.agent_folder = Path(__file__).parent / 'Agents'
        else:
            self.agent_folder = Path(agent_folder)
        agent_details = self.load_all_agent_details(self.agent_folder)
        agents = [self.convert_agent_details_to_agent(agent) for agent in agent_details]
        self.agents: dict[str, Agent] = {agent.get_id(): agent for agent in agents}
        self.default_agent = Agent(self.get_fully_tooled_llm_instance(), self.logger, self.tool_executor)

    def get_agent_names(self) -> list[str]:
        return list(self.agents.keys())

    def get_agents(self) -> dict[str, Agent]:
        return {agent_id: agent for agent_id, agent in self.agents.items()}

    def get_default_agent(self) -> Agent:
        return self.default_agent

    def get_agent(self, agent_id: str | None = None) -> Agent:
        if not agent_id or agent_id not in self.agents:
            return self.get_default_agent()
        return self.agents.get(agent_id)
