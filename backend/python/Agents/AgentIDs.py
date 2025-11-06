class AgentIDsClass:
    def __init__(self, workers: list[str] | None = None):
        self.ERROR = 'error'
        self.STOP = 'stop'
        self.SUPERVISOR = 'supervisor'
        self.USER = 'user'

        self.Special = [self.ERROR, self.STOP, self.SUPERVISOR, self.USER]
        if not workers:
            self.Workers = []
        else:
            self.Workers = workers
        self.All = self.Special + self.Workers

    def add(self, agent_id: str) -> None:
        agent_id = agent_id.lower()
        if agent_id in self.All:
            return
        self.All.append(agent_id)
        self.Workers.append(agent_id)


AgentIDs = AgentIDsClass()


def main():
    print(f'{__file__} is running...')


if __name__ == '__main__':
    main()
