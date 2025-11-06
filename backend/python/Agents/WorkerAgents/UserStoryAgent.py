from Agents.AgentFactory import add_agent_template
from Agents.LlmSingleton import get_llm_instance_with_tools
from Agents.RunnableAgent import RunnableAgent
from Tools.BaseTools import get_base_tools_by_name

name = 'User story agent'
description = 'This agent can turn high level requests from the user into detailed user stories.'
system_prompt = (
    'You are an AI user story agent.\n'
    'You have to transform the user\'s request into a propper user story that a team can then follow '
    'in order to achieve the user\'s goal.'
)
tool_names = []


def create_new_agent() -> RunnableAgent:
    llm = get_llm_instance_with_tools(get_base_tools_by_name(tool_names))
    return RunnableAgent(llm, name, description, system_prompt)


add_agent_template(name, create_new_agent)


def main():
    print(f'{__file__} is running...')


if __name__ == '__main__':
    main()
