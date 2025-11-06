import socket
from threading import Thread

from Agents.MultiAgentSystem import MultiAgentSystem


multi_agent_systems: dict[str, MultiAgentSystem] = {}


def start_streaming(stream, streaming_host: str, streaming_port: int):
    """
    Method used inside the answer_query service for streaming the generated answer at the streaming address
    This loops untill done is set and waits on each iteration for condition to notify
    """
    stream, condition, done = stream
    last_pos = stream.tell()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print('Waiting to connect to the user\'s message receiving server...')
        s.connect((streaming_host, streaming_port))
        print(f'Connected on {streaming_host}:{streaming_port}!')
        while True:
            with condition:
                if last_pos == stream.tell():
                    if done.is_set():
                        break
                    condition.wait()
                stream.seek(last_pos)
                new_data = f'{stream.read()}'
                if new_data:
                    s.sendall(new_data.encode())
                    last_pos = stream.tell()


def host_and_port_to_key(host: str, port: str | int) -> str:
    return f'{host}:{port}'


def answer_query(query: str, streaming_host: str, streaming_port: int) -> str:
    unique_key = host_and_port_to_key(streaming_host, streaming_port)

    if unique_key not in multi_agent_systems:
        multi_agent_systems[unique_key] = MultiAgentSystem()
    multi_agent_system = multi_agent_systems[unique_key]

    if not multi_agent_system.is_working:
        multi_agent_system.start_work()
        thread_work = lambda: start_streaming(multi_agent_system.stream, streaming_host, streaming_port)
        Thread(target=thread_work, daemon=True).start()

    multi_agent_system.add_user_input(query)
    return f'Agent will answer to {unique_key} ...'


def clear_history(streaming_host: str, streaming_port: int) -> bool:
    unique_key = host_and_port_to_key(streaming_host, streaming_port)
    if unique_key not in multi_agent_systems:
        return False
    return multi_agent_systems[unique_key].clear_history()


def main():
    print(f'{__file__} is running...')


if __name__ == '__main__':
    main()
