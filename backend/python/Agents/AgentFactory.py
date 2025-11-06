from typing import Callable, Any

from Agents.AgentIDs import AgentIDs


def default_template_function() -> None:
    return None


default_template: Callable[[], Any] = default_template_function


def set_default_template(template: Callable[[], Any]) -> None:
    global default_template
    default_template = template


agent_templates: dict[str, Callable[[], Any]] = {} # A dictionary with string key (agent id) and function value (function for creating a new instance of that agent)


def add_agent_template(agent_id: str | None, template: Callable[[], Any]) -> None:
    if not agent_id:
        return set_default_template(template)
    agent_id = agent_id.lower()
    AgentIDs.add(agent_id)
    agent_templates[agent_id] = template


def create_new_agent(agent_id: str | None = None):
    if not agent_id:
        return default_template()
    agent_id = agent_id.lower()
    if agent_id not in agent_templates:
        return default_template()
    return agent_templates[agent_id]()


def main():
    print(f'{__file__} is running...')


if __name__ == '__main__':
    main()
