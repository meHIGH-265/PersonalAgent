import json

from src.Agents.AgentLogic.AgentIDs import MyAgentIDs
from src.Agents.Brain.ToolLLM import ToolLLM
from src.Agents.Agent import Agent
from src.Agents.Tools.ToolManager import MyToolManager


class SupervisorAgent(Agent):
    @staticmethod
    def get_agent_names(worker_agents: list[Agent]) -> str:
        agent_names = ''
        for agent in worker_agents:
            agent_names += f' "{agent.name}",'
        agent_names = agent_names[:-1] + '.'
        return agent_names

    @staticmethod
    def get_agent_requirements(worker_agents: list[Agent]) -> str:
        agent_requirements = 'Here is what you need to know about the agents:\n'
        for agent in worker_agents:
            agent_requirements += f'{agent.name}: {agent.description}\n'
        return agent_requirements

    def __init__(self, worker_agents: list[Agent] | None = None):
        llm = ToolLLM.create_a_default_instance()

        if not worker_agents:
            self.solo_mission = True

            llm.bind_tools(MyToolManager.get_base_tools_by_name())
            name = 'Agent'
            description = 'Personal agent with tools'
            instructions = (
                'You are a helpfull AI assistant that can interact with the user\'s file environment.\n'
                'When asked to solve programming tasks, you use a layered architecture and you '
                'respect the single responsability principle by splitting the code into multiple files. '
                'Once you have an architecture in mind, check with the user if it is good and if you should proceed.\n'
                'You also test your work using pyunit and run those tests to check if your code works. '
                'For each separate file that you test, have a separate test file. '
                'Use logging inside your tests so you can determine easyer wher the tests failed if they somehow do. '
                'You don\'t need to ask permission from the user for testing. '
                'You should run tests before giving the final solution.\n\n'
                'You may change your default behaviour if the user specifically requests it.'
            )
        else:
            self.solo_mission = False

            llm.bind_tools({})
            name = 'Supervisor'
            description = 'This is the leader of the team.'
            instructions = (
                'You are the supervisor of a team of agents. '
                f'These are their IDs:{self.get_agent_names(worker_agents)}\n\n'
                
                'Your job is to coordinate the team to achieve the goals set by the user.\n\n'
                
                'Here is how you **must** communicate:\n'
                
                'You will receive a json dictionary where the keys are names of agents (or "user"), '
                'and the coresponding values are the messages you received from them.\n'
                
                'Your answers MUST allways be a single json dictionary where '
                'the keys are names of agents (or "user" or "stop") and '
                'the values are the messages you want to send them.\n'
                
                'You may send multiple messages at a time by simply including more keys in the same json dictionary.\n'
                
                'Send a message to the user whenever progress is made or whenever working on a task begins. '
                'You can also send the user information about problems that appear during work, '
                'but try to fix them together with the team. '
                'Only stop execution and ask for user help when the agents don\'t make any more progress.\n'
                
                'Sending a message to the user can be done by including a "user" or "stop" key in your answer. '
                'Use "user" for updates in the middle of the work (when there are still agents working on tasks) and '
                'use "stop" for when no agent is working.\n'
                
                f'\n{self.get_agent_requirements(worker_agents)}\n'
                
                'Not all agents are usefull or needed to complete some tasks. '
                'Plan ahead what agents will do what and in what order '
                '(they can work in parallel if they don\'t depend on someone elses progress), '
                'and send the user a message explaining the planned workflow.\n\n'
                
                'The agents can only see the messages you send to them, and not the others.\n'
                'You are responsible for formulating propper interogations for the agents by including all the details '
                'they need to complete their task.\n'
                'The agents can\'t see your conversation with other agents or the user, and '
                'the user can only see the "user" messages.\n'
                'Don\'t interogate any agent unless you have the information to formulate a task for them.\n\n'
                
                'Remember to not do work yourself, just coordinate the specialized agents to do the work.\n'
                
                'Remember to **allways** answer in the specified json format.'
            )

        super().__init__(llm, name, description, instructions)

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
        if self.solo_mission:
            answer = self.solve_task(supervisor_input_dict[MyAgentIDs.USER])
            return {MyAgentIDs.STOP: answer}

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
