from pathlib import Path


def create_new_agent(agent_name: str, template_path: Path | str | None = None) -> None:
    template_path: Path = Path(template_path or (Path(__file__).parent / 'Template.py'))

    def cammel_case(a_string: str, join_character: str = '') -> str:
        return join_character.join([s.capitalize() for s in f'{a_string}'.split(' ')])

    agent_name_with_spaces: str = cammel_case(agent_name, ' ')
    agent_name: str = cammel_case(agent_name)

    template_content = template_path.read_text(encoding='utf-8')

    # Name
    template_content = template_content.replace(
        'name: str = \'\'',
        f'name: str = \'{agent_name}\'',
        1
    )

    # Description
    article = 'an' if agent_name[0].lower() in 'aeiou' else 'a'
    template_content = template_content.replace(
        'description: str = \'\'',
        f'description: str = \'This agent is {article} {agent_name_with_spaces}.\'',
        1
    )

    # Instructions
    template_content = template_content.replace(
        'instructions: str = \'\'',
        f'instructions: str = (\n\t\'You are an AI {agent_name_with_spaces}.\'\n)',
        1
    )

    # Tools
    template_content = template_content.replace(
        'tool_names: list[str] = []',
        'tool_names: list[str] = []',
        1
    )

    file_path = f'{agent_name}GeneratorScript.py'
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(template_content)

    print(f'Script generated at: "{file_path}"')


def main():
    agent_name = 'pancake agent'

    template_path: Path = Path(__file__).parent / 'Template.py'
    create_new_agent(agent_name, template_path)


if __name__ == '__main__':
    main()
