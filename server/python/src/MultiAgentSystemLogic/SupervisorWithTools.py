from langchain_core.tools import BaseTool, StructuredTool
import json
from pydantic import BaseModel
from typing import Callable

from src.Agents.AgentLogic.AgentIDs import MyAgentIDs
from src.Agents.Brain.ToolLLM import ToolLLM
from src.Agents.Agent import Agent


class SupervisorAgent(Agent):

    @staticmethod
    def make_tool_from_agent(agent: Agent, submit_answer: Callable[[str], None]) -> BaseTool:
        class CallAgentInput(BaseModel):
            query: str

        def call_agent(query: str) -> str:
            agent.give_task(query, submit_answer)
            return 'I\'ll let you know when it\'s done.'

        call_agent_tool = StructuredTool.from_function(
            func=call_agent,
            name=f'call_{agent.get_id()}',
            description=f'{agent.description}.\nIt can: {agent.llm.tools.keys()}',
            args_schema=CallAgentInput
        )

        return call_agent_tool

    def submit_answer(self, agent_id: str) -> Callable[[str], None]:
        pass

    def __init__(self, worker_agents: list[Agent] | None = None):
        llm = ToolLLM.create_a_default_instance()
        name = 'Supervisor'
        description = 'This is the leader of the team.'
        instructions = (
            'You are the supervisor of a team of agents. '
            'Your job is to coordinate the team to achieve the goals set by the user.\n'

            'You can communicate with them by using your tools.\n'

            'If they respond that they will start working that means they will do it. '
            'You can ask them for something even if they didnt respond to your first task, '
            'but they will respond to tasks in the order they receive them.\n'

            'Your answers MUST allways be a single json dictionary where '
            'the keys are names of agents (or "user" or "stop") and '
            'the values are the messages you want to send them.\n'

            'Not all agents are usefull or needed to complete some tasks. '
            'Plan ahead what agents will do what and in what order '
            '(they can work in parallel if they don\'t depend on someone elses progress), '
            'and send the user a message explaining the planned workflow.\n'

            'The agents can only see the messages you send to them, and not the others.\n'
            'You are responsible for formulating propper interogations for the agents by including all the details '
            'they need to complete their task.\n'
            'The agents can\'t see your conversation with other agents or the user, and '
            'the user can only see the "user" messages.\n'
            'Don\'t interogate any agent unless you have the information to formulate a task for them.\n'

            'Remember to not do work yourself, just coordinate the specialized agents to do the work.'
        )

        super().__init__(llm, name, description, instructions)

        tools_by_name = {}
        for agent in worker_agents:
            call_agent_tool = self.make_tool_from_agent(agent, self.submit_answer(agent.get_id()))
            tool_name = call_agent_tool.name
            tools_by_name[tool_name] = call_agent_tool

        llm.bind_tools(tools_by_name)


    @staticmethod
    def parse_input(supervisor_input_dict: dict[str, str]) -> str:
        if not supervisor_input_dict:
            return '{}'

        supervisor_input = '{\n'

        for k, v in supervisor_input_dict.items():
            supervisor_input += f'\t"{k}": "{v}",\n'

        supervisor_input = supervisor_input[:-2]

        supervisor_input += '\n}'

        return supervisor_input

    @staticmethod
    def parse_answer(supervisor_answer: str) -> dict[str, str]:
        if supervisor_answer.startswith('```json') and supervisor_answer.endswith('```'):
            supervisor_answer = supervisor_answer[7:len(supervisor_answer) - 3]

        try:
            data = json.loads(supervisor_answer)
        except json.JSONDecodeError:
            print('json.JSONDecodeError')
            return {MyAgentIDs.STOP: f'{supervisor_answer}'}

        if type(data) is not dict:
            print('data is not dict')
            return {MyAgentIDs.STOP: f'{supervisor_answer}'}

        bad_keys = []
        for k, v in data.items():
            if not k or not v:
                bad_keys.append(k)
        for k in bad_keys:
            data.pop(k)

        parsed_answer = {f'{agent_id}'.lower(): f'{task}' for agent_id, task in data.items() if task}

        for agent_id in parsed_answer.keys():
            if agent_id not in MyAgentIDs.All:
                raise ValueError(f'{agent_id} is not a real agent. '
                                 f'Respond again ONLY using keys that you are allowed')

        return parsed_answer

    def distribute_tasks(self, supervisor_input_dict: dict[str, str]) -> dict[str, str]:
        supervisor_query = SupervisorAgent.parse_input(supervisor_input_dict)

        # Querying supervisor until he gives a parsable response
        fail_counter = 0
        while True:
            if fail_counter > 1:
                error_message = 'Supervisor failed to use propper formatting'
                parsed_answer = {MyAgentIDs.ERROR: error_message}
                break  # Failure break (will stop)
            answer = self.solve_task(supervisor_query)
            try:
                parsed_answer = SupervisorAgent.parse_answer(answer)
                break  # Success break (will continue)
            except ValueError as e:
                fail_counter += 1
                supervisor_query = f'{e}'

        # This section removes the empty messages from the supervisor response
        # Those appear when the supervisor answers with a dictionary with keys and empty values instead of omitting the key
        return {receiver: message for receiver, message in parsed_answer.items() if receiver and message}
