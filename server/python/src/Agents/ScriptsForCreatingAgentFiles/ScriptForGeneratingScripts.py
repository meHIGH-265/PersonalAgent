def create_new_agent(agent_name: str) -> None:
    def cammel_case(a_string: str, join_character: str = '') -> str:
        return join_character.join([s.capitalize() for s in f'{a_string}'.split(' ')])

    agent_name_with_spaces = cammel_case(agent_name, ' ')
    agent_name = cammel_case(agent_name)

    with open('Template.py', 'r', encoding='utf-8') as file:
        template_content = file.read()

    # Name
    template_content = template_content.replace(
        'name = None',
        f'name = \'{agent_name}\'',
        1
    )

    # Description
    article = 'an' if agent_name[0].lower() in 'aeiou' else 'a'
    template_content = template_content.replace(
        'description = None',
        f'description = \'This agent is {article} {agent_name_with_spaces}.\'',
        1
    )

    # Instructions
    template_content = template_content.replace(
        'instructions = None',
        f'instructions = (\n\t\'You are an AI {agent_name_with_spaces}.\'\n)',
        1
    )

    # Tools
    template_content = template_content.replace(
        'tool_names = None',
        'tool_names = []',
        1
    )

    file_path = f'{agent_name}GeneratorScript.py'
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(template_content)

    print(f'Script generated at: "./{file_path}"')


def main():
    agent_name = 'pancake agent'
    create_new_agent(agent_name)


if __name__ == '__main__':
    main()
