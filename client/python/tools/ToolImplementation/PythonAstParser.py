import ast
from typing import Any


class PythonAstParser:
    def __init__(self):
        pass

    @staticmethod
    def safe_unparse(node: ast.AST) -> str | None:
        try:
            return ast.unparse(node)
        except Exception:
            return None

    @staticmethod
    def pos_attrs(node: ast.AST) -> dict[str, Any]:
        d = {}
        for attr in ('lineno', 'col_offset', 'end_lineno', 'end_col_offset'):
            if hasattr(node, attr):
                d[attr] = getattr(node, attr)
        return d

    def serialize(self, node: Any, source: str) -> Any:
        """Recursively convert AST into a pure-Python structure."""
        if node is None:
            return None

        if isinstance(node, list):
            return [self.serialize(n, source) for n in node]

        if not isinstance(node, ast.AST):
            return node

        # Base dictionary for all nodes
        out = self.pos_attrs(node)

        out['node_type'] = type(node).__name__

        # Provide readable source excerpt
        try:
            out['source'] = ast.get_source_segment(source, node)
        except Exception:
            out['source'] = self.safe_unparse(node)

        # Special docstring handling
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            doc = ast.get_docstring(node, clean=False)
            if doc:
                out['docstring'] = doc

        # Process fields
        for field_name, value in ast.iter_fields(node):
            if isinstance(value, ast.AST):
                out[field_name] = self.serialize(value, source)
            elif isinstance(value, list):
                out[field_name] = [self.serialize(v, source) for v in value]
            else:
                out[field_name] = value

        return out

    def parse_python_source(self, source: str) -> dict[str, Any]:
        root = ast.parse(source)
        parsed_source = self.serialize(root, source)
        parsed_source['source'] = source
        return parsed_source

    @staticmethod
    def find_code_section_by_name_bfs(parsed_source: dict[str, Any], name: str) -> dict[str, Any]:
        search_queue: list[dict[str, Any]] = [parsed_source]
        while search_queue:
            section = search_queue.pop(0)
            if 'name' in section and section['name'] == name:
                return section
            if 'body' not in section:
                continue
            search_queue.extend(section['body'])
        return {}

    def find_code_section_by_name(self, source: str, name_stack: list[str] | str) -> dict[str, Any]:
        if isinstance(name_stack, str):
            name_stack = [name_stack]
        parsed_source = self.parse_python_source(source)
        while name_stack:
            section = self.find_code_section_by_name_bfs(parsed_source, name_stack.pop(0))
            if section:
                parsed_source = section
        return parsed_source

    @staticmethod
    def replace_lines(source: str, start_line: int, end_line: int, replacement: str) -> str:
        """
        start_line and end_line are both included in the interval that will be replaced
        Example: start_line = 5, end_line = 8
         -> Output: {lines 1 - 4} THEN {replacement} THEN {lines 9 - end_of_file}
        """

        result = ''

        lines = source.split('\n')
        for i in range(start_line - 1):
            result += f'{lines[i]}\n'
        result += replacement
        for i in range(end_line, len(lines)):
            result += f'\n{lines[i]}'

        return result

    def get_source_code_for_section_by_name(self, source: str, name_stack: list[str] | str) -> str:
        section = self.find_code_section_by_name(source, name_stack)['source']
        if section == source:
            return ''
        return section

    def replace_section_by_name(self, source: str, name_stack: list[str] | str, replacement: str) -> str:
        section = self.find_code_section_by_name(source, name_stack)

        if section['source'] == source:
            return source

        start_line = section['lineno']
        end_line = section['end_lineno']
        offset = section['col_offset']

        spacing = ' ' * offset
        replacement = f'{spacing}{replacement.replace('\n', f'\n{spacing}')}'

        return self.replace_lines(source, start_line, end_line, replacement)


def main():
    simple_example = '''
import math
from typing import List

class C:
    """A sample class"""
    x: int = 1
    def method(self, a: int) -> int:
        def nested(y: int) -> int:
            return y + 1
        return nested(a) + self.x

def f(z: List[int]) -> int:
    return sum(x for x in z if x > 0)
    '''

    with open('weird_code_sample.py', 'r', encoding='utf-8') as file:
        weird_code_sample = file.read()

    import json

    python_ast_parser = PythonAstParser()

    parsed_section = python_ast_parser.find_code_section_by_name(simple_example, ['C'])
    # print(json.dumps(parsed_section, indent=2))

    modified_section = python_ast_parser.replace_section_by_name(simple_example, ['C'], 'def C() -> None:\n\treturn')
    print(modified_section)


if __name__ == "__main__":
    main()
