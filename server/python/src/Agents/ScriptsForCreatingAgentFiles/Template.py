import json
from pathlib import Path


name = None
description = None
instructions = None
tool_names = None


def main():
    agent_data = {
        "name": name,
        "description": description,
        "instructions": instructions,
        "tool_names": tool_names
    }

    output_path = Path(f"../Agents/{name}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(agent_data, f, indent=2, ensure_ascii=False)

    print(f"Agent data saved to {output_path}")


if __name__ == '__main__':
    main()
