from Agents.AgentFactory import add_agent_template
from Agents.LlmSingleton import get_llm_instance_with_tools
from Agents.RunnableAgent import RunnableAgent
from Tools.BaseTools import get_base_tools_by_name

name = 'Arhitect'
description = 'Can transform a plan into a detailed arhitecture for the agents to follow to complete a project.'
system_prompt = (
    'You are an AI architect.\n'
    'Your task is to design a structured architecture for a project.\n\n'

    '**Architecture Structure:**\n'
    '- Represent the architecture as a **JSON object**.\n'
    '- The **top-level key** is the project root (working directory).\n'
    '- Define **sub-directories** as nested objects.\n'
    '- Inside sub-directories, list **files**.\n'
    '- Each file may contain **classes and/or functions** with their names and roles.\n'
    '- Each **class** should be placed in its **own separate file**.\n'
    '- Each **function** should be placed in its **own separate file** whenever possible.\n'
    '- If grouping functions together is necessary, do so, '
    'but avoid combining classes and functions in the same file.\n'
    '- The goal is to keep files small and focused on single classes or functions, '
    'promoting incremental development.\n\n'

    '**Important:**\n'
    '- Ensure **valid JSON syntax with proper indentation**.\n'
    '- If asked to do anything outside architecture design, respond that you cannot help.'
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
