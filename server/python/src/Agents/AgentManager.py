import json
from pathlib import Path
from typing import Any

from src.Agents.Agent import Agent
from src.Agents.Brain.ChatOpenAIFactory import ChatOpenAIFactory
from src.Agents.Brain.ToolLLM import ToolLLM
from src.Agents.Tools.Tool import Tool
from src.Agents.Tools.ToolExecutor import ToolExecutor
from src.Agents.Tools.ToolManager import ToolManager
from src.Logging.Logger import Logger


class AgentManager:
    @staticmethod
    def load_all_agent_details(agent_folder: Path) -> list[dict[str, Any]]:
        agent_details: list[dict[str, Any]] = []

        for json_file in agent_folder.glob('*.json'):
            with open(json_file, 'r', encoding='utf-8') as f:
                data: dict[str, Any] = json.load(f)
                agent_details.append(data)

        return agent_details

    def get_default_llm_instance(self) -> ToolLLM:
        return ToolLLM(
            self.chat_openai_factory.create(),
            ToolLLM.MyClassesToLangchainParser(),
            ToolLLM.LangchainToMyClassesParser()
        )

    def get_fully_tooled_llm_instance(self) -> ToolLLM:
        llm: ToolLLM = ToolLLM(
            self.chat_openai_factory.create(),
            ToolLLM.MyClassesToLangchainParser(),
            ToolLLM.LangchainToMyClassesParser()
        )
        llm.bind_tools(self.tool_manager.get_tools_by_name())
        return llm

    def convert_agent_details_to_agent(self, agent_details: dict[str, Any]) -> Agent:
        name: str = agent_details['name']
        description: str = agent_details['description']
        instructions: str = agent_details['instructions']
        tool_names: list[str] = agent_details['tool_names']

        llm: ToolLLM = self.get_default_llm_instance()
        tools: dict[str, Tool] = self.tool_manager.get_tools_by_name(tool_names)
        llm.bind_tools(tools)

        logger: Logger = self.logger
        tool_executor: ToolExecutor = self.tool_executor

        return Agent(llm, logger, tool_executor, name, description, instructions)

    def __init__(
            self,
            chat_openai_factory: ChatOpenAIFactory,
            logger: Logger,
            tool_executor: ToolExecutor,
            tool_manager: ToolManager,
            agent_folder: str | None = None
    ):
        self.chat_openai_factory: ChatOpenAIFactory = chat_openai_factory
        self.logger: Logger = logger
        self.tool_executor: ToolExecutor = tool_executor
        self.tool_manager: ToolManager = tool_manager
        self.agent_folder = Path(agent_folder or Path(__file__).parent / 'Agents')
        agent_details: list[dict[str, Any]] = self.load_all_agent_details(self.agent_folder)
        agents: list[Agent] = [self.convert_agent_details_to_agent(agent) for agent in agent_details]
        self.agents: dict[str, Agent] = {agent.get_id(): agent for agent in agents}
        self.default_agent = Agent(self.get_fully_tooled_llm_instance(), self.logger, self.tool_executor)

    def get_agent_names(self) -> list[str]:
        return list(self.agents.keys())

    def get_agents(self) -> dict[str, Agent]:
        return {agent_id: agent for agent_id, agent in self.agents.items()}

    def get_default_agent(self) -> Agent:
        return self.default_agent

    def get_agent(self, agent_id: str | None = None) -> Agent:
        return self.agents.get(agent_id, self.get_default_agent())
