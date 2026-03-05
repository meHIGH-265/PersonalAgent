from pathlib import Path
from threading import Lock, Thread
from typing import Callable, cast

from src.Agents.Brain.ToolLLM import ToolLLM
from src.Agents.Messages.Messages import Message, SystemMessage, UserMessage, ToolCall, ToolMessage, AIMessage
from src.Agents.Tools.ToolExecutor import ToolExecutor
from src.Logging.CustomLogging import Logger


class Agent:
    @staticmethod
    def get_default_agent_name() -> str:
        return 'Agent'

    @staticmethod
    def get_default_agent_system_prompt() -> str:
        default_agent_system_prompt_file_path = Path(__file__).parent / 'default_agent_system_prompt.md'

        with open(default_agent_system_prompt_file_path, 'r', encoding='utf-8') as system_prompt_file:
            default_agent_system_prompt = system_prompt_file.read()

        return default_agent_system_prompt

        # return (
        #     'You are a helpful AI assistant with access to tools.\n'
        #
        #     'When calling a tool:\n'
        #     '\tAlways include a brief, explicit summary of what you learned from previous tool calls and '
        #     'what you intend to accomplish with the tools you call then.\n'
        #     '\tYou may call multiple tools in a single message when appropriate.\n'
        #     '\tTools are executed in the order they are listed, so you may chain dependent actions '
        #     '(e.g., write a file and then execute it) within the same message.\n'
        #
        #     'Prefer strategic and context-aware tool usage:\n'
        #     '\tFavor tools that provide structured or high-level context '
        #     'over tools that return large, unfiltered outputs.\n'
        #     '\tAvoid "lazy" usage of tools that dump excessive content without first narrowing scope.\n'
        #     '\tWhen working with codebases, first inspect file structure '
        #     '(e.g., directories, class names, function signatures) before reading full file contents.\n'
        #     '\tRead only the specific functions, classes, or sections relevant to the task whenever possible.\n'
        #
        #     'Be deliberate, efficient, and explicit about your reasoning behind each tool call.'
        # )

    class ShouldPause(Exception):
        pass

    def __init__(
            self,
            llm: ToolLLM,
            logger: Logger,
            tool_executor: ToolExecutor,
            name: str | None = None,
            description: str | None = None,
            instructions: str | None = None
    ):
        # LLM
        self.llm = llm

        # Logger
        self.logger = logger

        # Tool Manager
        self.tool_executor = tool_executor

        # Name
        if not name:
            self.name = f'{self.get_default_agent_name()}'
        else:
            self.name = f'{name}'

        # Description
        if not description:
            self.description = ''
        else:
            self.description = f'{description}'

        # System prompt
        if not instructions:
            self.instructions = SystemMessage(self.get_default_agent_system_prompt())
        else:
            self.instructions = SystemMessage(f'{instructions}')

        # Message history
        self.message_history: list[Message] = [self.instructions]
        self.message_history_lock = Lock()

        # Task queue -> only use append and pop(0) !!!
        self.current_task: str | None = None
        self.tasks: list[tuple[str, Callable[[str], None], Callable[[str], None]]] = []
        self.tasks_lock = Lock()

        # Function for submitting answers. It is permanently stored so that it can be used in resume situations
        self.submit_final_answer: Callable[[str], None] = lambda _ : None
        self.submit_partial_answer: Callable[[str], None] = lambda _ : None

        # Working state
        self.working = False
        self.working_state_lock = Lock()
        self.should_pause = False

    def is_working(self) -> bool:
        with self.working_state_lock:
            return self.working

    def set_working_state(self, working: bool) -> None:
        """
        This always clears the should_pause flag when called,
        no matter the argument given
        """
        with self.working_state_lock:
            self.working = working
            self.should_pause = False

    def add_task(
            self, task: str,
            submit_final_answer: Callable[[str], None] = lambda _ : None,
            submit_partial_answer: Callable[[str], None] = lambda _ : None
    ) -> None:
        if not task:
            return
        with self.tasks_lock:
            self.tasks.append((task, submit_final_answer, submit_partial_answer))

    def get_next_task(self) -> tuple[str | None, Callable[[str], None], Callable[[str], None]]:
        with self.tasks_lock:
            if not self.tasks:
                return None, lambda _ : None, lambda _ : None
            return self.tasks.pop(0)

    def start_work(self) -> None:
        def work() -> None:
            if self.is_working():
                return
            self.set_working_state(True)

            try:
                self.resume_last_task_if_not_complete()

                next_task, self.submit_final_answer, self.submit_partial_answer = self.get_next_task()
                while next_task:
                    self.submit_final_answer(self.solve_task(next_task))
                    next_task, self.submit_final_answer, self.submit_partial_answer = self.get_next_task()
            except self.ShouldPause as _:
                pass

            self.set_working_state(False)

        Thread(target=work, daemon=True).start()

    def handle_partial_answer(self, partial_answer: AIMessage) -> None:
        if not partial_answer.get_tool_calls():
            return

        message_content = partial_answer.get_content()
        if message_content:
            self.submit_partial_answer(message_content)

    def complete_chat(self) -> AIMessage:
        # Check if the execution should pause
        with self.working_state_lock:
            if self.should_pause:
                raise self.ShouldPause

        # Both appends to the message history and returns the next message generated by AI
        # This is only one iteration of invoking the llm
        # It doesn't run any tools, just generates an answer that might contain tool calls or just plain content
        # There is no loop in this function

        ai_message = self.llm.complete_chat(self.message_history)
        self.message_history.append(ai_message)

        self.handle_partial_answer(ai_message)

        return ai_message

    def complete_chat_until_no_tools_are_called(self) -> AIMessage:
        # Invoke LLM to get first tool calls
        # Add AI's initial response to messages
        ai_message = self.complete_chat()

        # Process tool calls and append their outputs
        while True:
            # Get tool calls
            tool_calls: list[ToolCall] = ai_message.get_tool_calls()

            if not tool_calls:
                # If no tool was called this iteration of the while, then we break
                break

            # Iterate through tool calls
            for tool_call in tool_calls:
                # Run every tool called and append their result to the message history
                tool_msg: ToolMessage = self.tool_executor.call_tool(tool_call)
                self.message_history.append(tool_msg)

            # Invoke LLM again for potentially the final answer or maybe some more tool calls
            ai_message = self.complete_chat()

        return ai_message

    def resume_last_task_if_not_complete(self) -> None:
        with self.message_history_lock:
            # Check the last message and it's type
            last_message = self.message_history[-1]
            last_message_type = type(last_message)

            if last_message_type is SystemMessage:
                # last message is the system message (no AI intervention needed)
                return
            if last_message_type is AIMessage and not cast(AIMessage, last_message).get_tool_calls():
                # last message is an AI message without tool calls (also no AI intervention needed)
                return

            # AI intervention needed
            ai_msg = self.complete_chat_until_no_tools_are_called()

        log_msg = f'\n\ntask:\n{self.current_task}\n\nai_response:\n{ai_msg.get_content()}'
        self.logger.log(log_msg, who=self.name, use_separator=True)

        self.current_task = None

        # Submit answer with saved function
        self.submit_final_answer(ai_msg.get_content())

    # PROTECTED

    def solve_task(self, task: str) -> str:
        self.current_task = task

        with self.message_history_lock:
            # Convert the Task into Message type
            self.message_history.append(UserMessage(task))

            # Repeatedly invoke the llm untill he answers without tool calls
            ai_msg = self.complete_chat_until_no_tools_are_called()

        log_msg = f'\n\ntask:\n{self.current_task}\n\nai_response:\n{ai_msg.get_content()}'
        self.logger.log(log_msg, who=self.name, use_separator=True)

        self.current_task = None

        return ai_msg.get_content()

    # PUBLIC

    def get_id(self) -> str:
        return self.name.lower().replace(' ', '_')

    def give_task(
            self, task: str,
            submit_final_answer: Callable[[str], None] = lambda _ : None,
            submit_partial_answer: Callable[[str], None] = lambda _ : None
    ) -> None:
        if not task:
            return
        self.add_task(task, submit_final_answer, submit_partial_answer)

        if not self.is_working():
            self.start_work()

    def pause_work(self) -> None:
        with self.working_state_lock:
            if not self.working:
                return
            self.should_pause = True

    def resume_work(self) -> None:
        self.start_work()

    def clear_history(self) -> None:
        self.pause_work()
        with self.message_history_lock:
            with self.tasks_lock:
                self.message_history.clear()
                self.message_history.append(self.instructions)
                self.tasks.clear()
