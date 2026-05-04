from json import load
from pathlib import Path
from typing import Any

from src.Agents.Tools.Tool import Tool


TYPE_MAP: dict[str, type] = {'any': object} | {_type.__name__: _type for _type in [bool, dict, float, int, list, str]}


class ToolManager:
    @staticmethod
    def load_all_tool_specs(tool_folder: Path) -> list[dict[str, Any]]:
        tool_specs: list[dict[str, Any]] = []

        for json_file in tool_folder.glob('*.json'):
            with open(json_file, 'r', encoding='utf-8') as f:
                data: dict[str, Any] = load(f)
                tool_specs.append(data)

        return tool_specs

    @staticmethod
    def convert_tool_spec_to_tool(tool_spec: dict[str, Any]) -> Tool:
        name: str = tool_spec['name']
        description: str = tool_spec['description']
        args_schema: dict[str, type] = {arg_name: TYPE_MAP[arg_type] for arg_name, arg_type in tool_spec['args_schema'].items()}
        return Tool(name, description, args_schema)

    def __init__(self, tool_folder: Path | str | None = None):
        self.tool_folder = Path(tool_folder or Path(__file__).parent / 'Tools')
        tool_specs: list[dict[str, Any]] = self.load_all_tool_specs(self.tool_folder)
        tools: list[Tool] = [self.convert_tool_spec_to_tool(tool) for tool in tool_specs]
        self.tools: dict[str, Tool] = {tool.get_name(): tool for tool in tools}

    def get_tools_by_name(self, names: list[str] | None = None) -> dict[str, Tool]:
        """
        If names is None, this returns all the tools available
        If name is a list, this only returns the tools whose names appear in the list
        (For an empty list this returns an empty dictionary)
        """
        if names is None:
            return self.tools
        return {the_name: the_tool for the_name, the_tool in self.tools.items() if the_name in names}
