import ast
import json
from typing import Any


class PythonAstParser:
    @staticmethod
    def __safe_unparse(node: ast.AST) -> str | None:
        try:
            return ast.unparse(node)
        except Exception:
            return None

    @staticmethod
    def __pos_attrs(node: ast.AST) -> dict[str, Any]:
        d = {}
        for attr in ('lineno', 'col_offset', 'end_lineno', 'end_col_offset'):
            if hasattr(node, attr):
                d[attr] = getattr(node, attr)
        return d

    def __serialize(self, node: Any, source: str) -> Any:
        """Recursively convert AST into a pure-Python structure."""
        if node is None:
            return None

        if isinstance(node, list):
            return [self.__serialize(n, source) for n in node]

        if not isinstance(node, ast.AST):
            return node

        # Base dictionary for all nodes
        out = self.__pos_attrs(node)

        out['node_type'] = type(node).__name__

        # Provide readable source excerpt
        try:
            out['source'] = ast.get_source_segment(source, node)
        except Exception:
            out['source'] = self.__safe_unparse(node)

        # Special docstring handling
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            doc = ast.get_docstring(node, clean=False)
            if doc:
                out['docstring'] = doc

        # Process fields
        for field_name, value in ast.iter_fields(node):
            if isinstance(value, ast.AST):
                out[field_name] = self.__serialize(value, source)
            elif isinstance(value, list):
                out[field_name] = [self.__serialize(v, source) for v in value]
            else:
                out[field_name] = value

        return out

    def __parse_python_source(self, source: str) -> dict[str, Any]:
        root = ast.parse(source)
        parsed_source = self.__serialize(root, source)
        parsed_source['source'] = source
        return parsed_source

    def __init__(self, python_source: str):
        self.parsed_python_source: dict[str, Any] = self.__parse_python_source(python_source)

    @staticmethod
    def __find_code_section_by_name_bfs(parsed_python_source: dict[str, Any], name: str) -> dict[str, Any]:
        if not name or name == '.' or not parsed_python_source:
            return parsed_python_source

        queue: list[dict[str, Any]] = [parsed_python_source]

        while queue:
            node = queue.pop(0)
            if node.get('name', '') == name:
                return node
            queue.extend(node.get('body', []))

        return {}

    def __find_code_section_by_name_with_extra_info_on_failure(self, name_stack: list[str] | str) -> dict[str, Any]:
        if isinstance(name_stack, str):
            name_stack = [name_stack]

        found = []
        crt_node = self.parsed_python_source

        for name in name_stack:
            next_node = self.__find_code_section_by_name_bfs(crt_node, name)
            if next_node:
                found.append(name)
                crt_node = next_node
            else:
                return {
                    'error_type': 'warning',
                    'error_message': f'Couldn\'t find one of the named code sections.',
                    'code_section_not_found': name,
                    'code_sections_found': found,
                    'parsed_section': crt_node
                }

        return crt_node

    def __get_source_code_for_section_by_name_with_extra_info_on_failure(self, name_stack: list[str] | str) -> str:
        parsed_section = self.__find_code_section_by_name_with_extra_info_on_failure(name_stack)

        if 'source' in parsed_section:
            return parsed_section['source']

        if 'parsed_section' in parsed_section:
            if 'source' in parsed_section['parsed_section']:
                parsed_section['source'] = parsed_section['parsed_section']['source']
            parsed_section.pop('parsed_section')

        return json.dumps(parsed_section, indent=2)

    def find_code_section_by_name(self, name_stack: list[str] | str) -> dict[str, Any]:
        if isinstance(name_stack, str):
            name_stack = [name_stack]

        crt_node = self.parsed_python_source

        for name in name_stack:
            crt_node = self.__find_code_section_by_name_bfs(crt_node, name)

        return crt_node

    def get_source_code_for_section_by_name(self, name_stack: list[str] | str) -> str:
        parsed_section = self.find_code_section_by_name(name_stack)

        if 'source' in parsed_section:
            return parsed_section['source']

        return ''

    @staticmethod
    def __replace_lines(source: str, start_line: int, end_line: int, replacement: str) -> str:
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

    def replace_section_by_name(self, name_stack: list[str] | str, replacement: str) -> str:
        parsed_section = self.find_code_section_by_name(name_stack)

        source = ''

        try:
            source = self.parsed_python_source['source']
            start_line = parsed_section['lineno']
            end_line = parsed_section['end_lineno']
            offset = parsed_section['col_offset']
        except KeyError:
            return source

        spacing = ' ' * offset
        replacement = f'{spacing}{replacement.replace('\n', f'\n{spacing}')}'

        return self.__replace_lines(source, start_line, end_line, replacement)


def main():
    simple_example = '''
import math
from typing import List

class C(A, B):
    """A sample class"""
    x: int = 1
    def method(self, a: int) -> int:
        def nested(y: int) -> int:
            return y + 1
        return nested(a) + self.x

def nested(z: List[int]) -> int:
    return sum(x for x in z if x > 0)
    '''

    with open('weird_code_sample.py', 'r', encoding='utf-8') as file:
        weird_code_sample = file.read()

    python_ast_parser = PythonAstParser(simple_example)

    # parsed_section = python_ast_parser.__find_code_section_by_name('asd')
    # print(json.dumps(parsed_section, indent=2))

    modified_section = python_ast_parser.replace_section_by_name(['C', 'nested'], 'def replacement_method():\n\tpass')
    print(modified_section)


if __name__ == "__main__":
    main()
