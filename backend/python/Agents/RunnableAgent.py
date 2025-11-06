from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, ToolMessage
from threading import Lock, Thread
from typing import Callable

from Agents.AgentFactory import set_default_template
from Agents.LlmSingleton import LLM, get_llm_instance_with_tools
from Utils.CustomLogging import log
from Utils.EnvironmentVariableManager import get_default_agent_system_prompt, get_default_agent_name


class RunnableAgent:
    def __init__(self, llm: LLM,
                 name: str | None = None,
                 description: str | None = None,
                 instructions: str | SystemMessage | None = None):
        # Name
        if name:
            self.name = f'{name}'
        else:
            self.name = f'{get_default_agent_name()}'

        # Description
        if not description:
            self.description = ''
        else:
            self.description = f'{description}'

        # System prompt
        if not instructions:
            self.instructions = SystemMessage(get_default_agent_system_prompt())
        elif type(instructions) is SystemMessage:
            self.instructions = instructions
        elif type(instructions) is str:
            self.instructions = SystemMessage(instructions)
        else:
            self.instructions = SystemMessage(get_default_agent_system_prompt())

        # LLM
        self.llm = llm

        # Message history
        self.message_history: list[BaseMessage] = [self.instructions]
        self.message_history_lock = Lock()

        # Task queue
        self.tasks = []
        self.tasks_lock = Lock()

    def solve_next_task(self, task: str | None = None) -> str:
        with self.message_history_lock:
            if not task:
                with self.tasks_lock:
                    if not self.tasks:
                        return ''
                    task = self.tasks.pop(0)
            self.message_history.append(HumanMessage(task))

            # Invoke LLM to get tool calls
            ai_msg = self.llm.invoke(self.message_history)

            # Add AI's initial response to messages
            self.message_history.append(ai_msg)

            # Process tool calls and append their outputs
            while True:
                tool_has_been_called = False
                for tool_call in ai_msg.tool_calls:
                    tool_has_been_called = True
                    selected_tool = self.llm.tools.get(tool_call['name'].lower(), None)
                    if not selected_tool:
                        self.message_history.append(ToolMessage(f'The tool "{tool_call['name']}" doesn\'t exist! Don\'t call it again'))
                        continue
                    tool_msg = selected_tool.invoke(tool_call)
                    self.message_history.append(tool_msg)

                if not tool_has_been_called:
                    break

                ai_msg = self.llm.invoke(self.message_history)
                self.message_history.append(ai_msg)

        log(f'{self.name}:\n\ntask:\n{task}\n\nai_response:\n{ai_msg.content}')

        return ai_msg.content

    def solve_task_async(self, task: str, submit_answer: Callable[[str], None]) -> None:
        with self.tasks_lock:
            self.tasks.append(task)
        thread_work = lambda: submit_answer(self.solve_next_task())
        Thread(target=thread_work, daemon=True).start()

    def clear_history(self) -> None:
        with self.message_history_lock and self.tasks_lock:
            self.message_history.clear()
            self.message_history.append(self.instructions)
            self.tasks.clear()


def default_template() -> RunnableAgent:
    return RunnableAgent(get_llm_instance_with_tools(MOCK=True))


set_default_template(default_template)


def main():
    print(f'{__file__} is running...')


if __name__ == '__main__':
    main()
