from typing import Any

from src.Agents.AgentManager import AgentManager
from src.Streaming.Streamer import Streamer


class SingleAgentServices:
    def __init__(self, agent_manager: AgentManager, streamer: Streamer):
        self.agent_manager = agent_manager
        self.streamer = streamer

    def call_agent(
            self, query: str,
            agent_id: str | None = None,
            streaming_host: str | None = None,
            streaming_port: int | None = None
    ) -> None:
        if streaming_host is None or streaming_port is None:
            self.agent_manager.get_agent(agent_id).give_task(query)
            return

        def submit_final_answer(answer: str) -> None:
            self.streamer.send_data(answer)
            self.streamer.stop_streaming()

        def submit_partial_answer(answer: str) -> None:
            self.streamer.send_data(answer)

        self.streamer.start_streaming(streaming_host, streaming_port)
        self.agent_manager.get_agent(agent_id).give_task(query, submit_final_answer, submit_partial_answer)

    def clear_history(self, *args, **kwargs) -> Any:
        pass
