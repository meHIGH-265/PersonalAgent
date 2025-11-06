from io import StringIO
from threading import Condition, Event, Lock, Thread

from Agents.AgentFactory import create_new_agent
from Agents.AgentIDs import AgentIDs
from Agents.RunnableAgent import RunnableAgent
from Agents.Supervisor import SupervisorAgent
from Agents.WorkerAgentManagerSystem.UsedWorkers import use_workers


class MultiAgentSystem:
    def __init__(self, agent_ids: list[str] | None = None):
        if agent_ids is None:
            agent_ids = AgentIDs.Workers

        # The worker agents included in the multi-agent system
        self.agents: dict[str, RunnableAgent] = {agent_id: create_new_agent(agent_id) for agent_id in agent_ids if agent_id in AgentIDs.Workers}

        self.supervisor_input: dict[str, str] = {}
        self.supervisor_input_lock = Lock()
        self.supervisor_input_not_empty_condition = Condition()

        self.is_working = False
        self.is_working_lock = Lock()

        self.stream = StringIO(), Condition(), Event()
        self.supervisor = SupervisorAgent([agent for agent in self.agents.values()])

    def task_agent(self, task: str, agent_id: str) -> None:
        """
        Sends a task to one of the worker agents.
        The agent will take care of the task on a separate thread
        and submit the answer when it's done to the supervisor input dictionary
        """
        if agent_id not in self.agents:
            return

        def submit_answer(answer: str) -> None:
            with self.supervisor_input_not_empty_condition:
                with self.supervisor_input_lock:
                    self.supervisor_input[agent_id] = answer
                self.supervisor_input_not_empty_condition.notify()

        self.agents[agent_id].solve_task_async(task, submit_answer)

    @staticmethod
    def split_supervisor_answer(parsed_answer: dict[str, str]) -> tuple[dict[str, str], dict[str, str]]:
        """
        splits the supervisor answer in messages for the agents and for the user
        """
        special_agent_inbox = {special_agent_id: message for special_agent_id, message in parsed_answer.items()
                               if special_agent_id in AgentIDs.Special}
        worker_agent_inbox = {special_agent_id: task for special_agent_id, task in parsed_answer.items()
                              if special_agent_id in AgentIDs.Workers}
        return special_agent_inbox, worker_agent_inbox

    def handle_special_agent_inbox(self, special_agent_inbox: dict[str, str],
                                   stream: StringIO | None = None,
                                   condition: Condition | None = None) -> None:
        """
        Sends the messages that should reach the user through the stream
        """

        if stream is None or condition is None:
            stream, condition, done = self.stream

        # Send the user a message
        if AgentIDs.USER in special_agent_inbox:
            user_message = special_agent_inbox[AgentIDs.USER]
            special_agent_inbox.pop(AgentIDs.USER)
            with condition:
                stream.write(f'{user_message}\n\n')
                stream.flush()
                condition.notify()

        # Send the user the last message and end session
        if AgentIDs.STOP in special_agent_inbox:
            stop_message = special_agent_inbox[AgentIDs.STOP]
            with condition:
                stream.write(f'{stop_message}\n\n')
                stream.flush()
                condition.notify()

        # Send the user the error and end session
        if AgentIDs.ERROR in special_agent_inbox:
            error_message = special_agent_inbox[AgentIDs.ERROR]
            with condition:
                stream.write(f'Error:\n{error_message}\n\n')
                stream.flush()
                condition.notify()

    def work(self) -> None:
        """
        Starts a feedback loop between the supervisor, the user and the worker agents
        """

        stream, condition, done = self.stream

        with self.is_working_lock:
            if done.is_set:
                done.clear()
            self.is_working = True

        while self.is_working:
            with self.supervisor_input_not_empty_condition:
                while not self.supervisor_input:
                    self.supervisor_input_not_empty_condition.wait()
            with self.supervisor_input_lock:
                supervisor_input = { k: v for k, v in self.supervisor_input.items() }
                self.supervisor_input.clear()

            parsed_answer = self.supervisor.distribute_tasks(supervisor_input)

            special_agent_inbox, worker_agent_inbox = self.split_supervisor_answer(parsed_answer)

            self.handle_special_agent_inbox(special_agent_inbox, stream, condition)
            if AgentIDs.STOP in special_agent_inbox or AgentIDs.ERROR in special_agent_inbox:
                break

            # Send all workers their task
            for agent_id, task in worker_agent_inbox.items():
                self.task_agent(task, agent_id)

        # Close the stream
        with self.is_working_lock:
            done.set()
            self.is_working = False

        # Notify all stream readers
        with condition:
            condition.notify_all()

    def start_work(self) -> None:
        """
        Begins the work cycle on a new thread
        """
        Thread(target=lambda: self.work()).start()

    def add_user_input(self, user_input: str) -> None:
        """
        This method is called when the user sends a message towards the system.
        This method is well synchronised and handles the cases where there are still unanswered user queries
        """
        with self.supervisor_input_not_empty_condition:
            with self.supervisor_input_lock:
                if AgentIDs.USER not in self.supervisor_input:
                    self.supervisor_input[AgentIDs.USER] = user_input
                else:
                    self.supervisor_input[AgentIDs.USER] += f'\n\n{user_input}'
            self.supervisor_input_not_empty_condition.notify()

    def clear_history(self) -> bool:
        """
        Clears the memory of ALL the agents including the supervisor,
        and returns true if at least one of them had memory to clear
        or false if the agents have no memory already

        This also stops the execution of the current task
        """

        # This is a legacy print that was created to find out why
        # this function was being called when it wasn't supposed to
        # For the bachelor degree the arhive sent contained this log
        # This MUST stay here FOREVER!
        print('\n\n#####################################'
              '\nTHIS WAS CALLED FOR SOME FKING REASON\n'
              '#####################################\n\n')

        with self.is_working_lock:
            self.is_working = False

            history_was_cleared = self.supervisor.clear_history()

            for agent in self.agents.values():
                history_was_cleared = history_was_cleared or agent.clear_history()

        return history_was_cleared


use_workers()


def main():
    MAS = MultiAgentSystem()

    print(MAS.supervisor.instructions.content)

    print(f'{__file__} is running...')


if __name__ == '__main__':
    main()
