def generate_file_name(agent_name: str | None = None) -> str:
    return ''.join([s.capitalize() for s in f'{agent_name}'.split(' ')])


def use_agent(agent_name: str | None = None, should_use_agent: bool = True) -> None:
    print(f'use_agent(agent_name={agent_name}, should_use_agent={should_use_agent})')

    if not agent_name:
        return

    with open('UsedWorkers.py', 'r', encoding='utf-8') as file:
        used_workers_content = file.read()

    file_name = generate_file_name(agent_name)
    new_used_workers_content = used_workers_content.replace(f'import Agents.WorkerAgents.{file_name}\n', '')
    if should_use_agent:
        new_used_workers_content = f'import Agents.WorkerAgents.{file_name}\n{new_used_workers_content}'

    # print(new_used_workers_content)
    with open('UsedWorkers.py', 'w', encoding='utf-8') as file:
        file.write(new_used_workers_content)


def unuse_agent(agent_name: str | None = None) -> None:
    print(f'unuse_agent(agent_name={agent_name})')

    if not agent_name:
        return

    use_agent(agent_name, False)


def create_new_agent(agent_name: str | None = None, should_use_agent: bool = False) -> None:
    print(f'create_new_agent(agent_name={agent_name}, should_use_agent={should_use_agent})')

    if not agent_name:
        return

    with open('DefaultTemplate.py', 'r', encoding='utf-8') as file:
        template_content = file.read()

    # Name
    template_content = template_content.replace('name = None',
                                                f'name = \'{agent_name.capitalize()}\'',
                                                1)
    # Role
    template_content = template_content.replace('role = None',
                                                f'role = \'{agent_name.lower()}\'',
                                                1)
    # ID
    template_content = template_content.replace('agent_id = None',
                                                f'agent_id = \'{agent_name.lower()}\'',
                                                1)
    # Description
    article = 'an' if agent_name[0].lower() in 'aeiou' else 'a'
    template_content = template_content.replace('description = None',
                                                f'description = \'This agent is {article} {agent_name.lower()}.\'',
                                                1)
    # System prompt
    template_content = template_content.replace('system_prompt = None',
                                                f'system_prompt = (\n\t\'You are an AI {agent_name.lower()}.\'\n)',
                                                1)
    # Tools
    template_content = template_content.replace('tool_names = None',
                                                'tool_names = []',
                                                1)

    # print(template_content)
    folder = '../WorkerAgents'
    file_path = f'{folder}/{generate_file_name(agent_name)}.py'
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(template_content)

    use_agent(agent_name, should_use_agent)


def main():
    print(f'{__file__} is running...')

    agent_name = 'user story agent'
    create_new_agent(agent_name, True)


if __name__ == '__main__':
    main()
