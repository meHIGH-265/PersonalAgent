from json import dumps
from pathlib import Path
from typing import Any


name: str = ''
description: str = ''
instructions: str = ''
tool_names: list[str] = []


def main():
    agent_data: dict[str, Any] = {
        "name": name,
        "description": description,
        "instructions": instructions,
        "tool_names": tool_names
    }

    output_path: Path = Path(__file__).parents[1] / 'Agents' / f'{name}.json'

    output_path.write_text(dumps(agent_data, indent=2), encoding='utf-8')

    print(f"Agent data saved to {output_path}")


if __name__ == '__main__':
    main()
