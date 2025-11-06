from Agents.AgentFactory import add_agent_template
from Agents.LlmSingleton import get_llm_instance_with_tools
from Agents.RunnableAgent import RunnableAgent
from Tools.BaseTools import get_base_tools_by_name

name = 'Planner'
description = 'This agent can come up with a detailed step by step plan based on a user story in order to achieve the user\'s goal.'
system_prompt = (
	'You are an AI planner.\n'
    'Take the user\'s request and transform it into a detailed step by step plan to achieve the goal.'
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
