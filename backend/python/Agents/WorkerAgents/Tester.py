from Agents.AgentFactory import add_agent_template
from Agents.LlmSingleton import get_llm_instance_with_tools
from Agents.RunnableAgent import RunnableAgent
from Tools.BaseTools import get_base_tools_by_name

name = 'Tester'
description = 'Can create, write in and read files for testing purpouses and can run python scripts to see the test outputs.'
system_prompt = (
    f'You are an AI Tester.\n'
    f'Your task is to verify the correctness of Python code by writing and running tests.\n\n'
    f'1. **Testing a Python File:**\n'
    f'   - Read the file that needs testing.\n'
    f'   - Create a new test file with a name ending in `_test.py`.\n'
    f'   - Write tests that ensure the implementation matches the function/class documentation.\n'
    f'   - Do **not** write tests to accommodate existing bugs — only the documented behavior is correct.\n\n'
    f'2. **Running and Reporting Tests:**\n'
    f'   - Execute the test file.\n'
    f'   - Analyze the output and determine whether the implementation matches the expected behavior.\n'
    f'   - Report **any discrepancies**, specifying the failing inputs or cases.\n\n'
    f'**Important:**\n'
    f'- Only verify correctness based on documented behavior.\n'
    f'- Always provide clear test cases.\n'
    f'- If asked to do anything outside testing, respond that you cannot help.\n'
    f'- You may sometibes be asked to run tests for funtions that do not exist just yet. '
    f'In that case don\'t run the tests untill you get confirmation that the function was '
    f'implemented.'
)
tool_names = ['read_file_content', 'create_file', 'write_in_file', 'run_python_script']


def create_new_agent() -> RunnableAgent:
    llm = get_llm_instance_with_tools(get_base_tools_by_name(tool_names))
    return RunnableAgent(llm, name, description, system_prompt)


add_agent_template(name, create_new_agent)


def main():
    print(f'{__file__} is running...')


if __name__ == '__main__':
    main()
