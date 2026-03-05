from pathlib import Path
from typing import Any

from ToolImplementation.PythonAstParser import PythonAstParser


class ProjectTree:
    def __build_project_tree(self, root_path: str | Path) -> dict[str, Any]:
        """
        root_path: directory to scan
        parse_file_to_dict: function(path:str) -> structured AST dict
        """
        root = Path(root_path).resolve()
        return self.__process_directory(root)
    
    def __process_directory(self, path: Path) -> dict[str, Any]:
        children = []
    
        for child in sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name)):
            if child.is_dir():
                children.append(self.__process_directory(child))
    
            elif child.suffix == '.py':
                children.append(self.__process_python_file(child))
    
            else:
                children.append(self.__process_non_python_file(child))
    
        return {
            'name': path.name,
            'type': 'directory',
            'children': children
        }
    
    @staticmethod
    def __process_non_python_file(path: Path) -> dict[str, Any]:
        return {
            'name': path.name,
            'type': 'file'
        }
    
    def __process_python_file(self, path: Path) -> dict[str, Any]:
        with open(path, 'r', encoding='utf-8') as python_file:
            content = python_file.read()
    
        classes = []
        functions = []
    
        for node in PythonAstParser(content).parsed_python_source.get('body', []):
            node_type = node.get('node_type')
    
            if node_type == 'ClassDef':
                classes.append(self.__extract_class(node))
    
            elif node_type == 'FunctionDef':
                functions.append(self.__extract_function(node))
    
        processed_file = {
            'name': path.name,
            'type': 'python_file'
        }
        if classes:
            processed_file['classes'] = classes
        if functions:
            processed_file['functions'] = functions
        return processed_file
    
    def __extract_class(self, node: dict[str, Any]) -> dict[str, Any]:
        bases = [base.get('id') if base.get('node_type') == 'Name' else base.get('source') for base in node.get('bases', [])]
        classes = []
        functions = []
    
        for item in node.get('body', []):
            node_type = item.get('node_type')
    
            if node_type == 'ClassDef':
                classes.append(self.__extract_class(item))
    
            elif node_type == 'FunctionDef':
                functions.append(self.__extract_function(item))
    
        processed_class = {
            'name': node.get('name'),
            'type': 'class'
        }
        if bases:
            processed_class['bases'] = bases
        if classes:
            processed_class['classes'] = classes
        if functions:
            processed_class['functions'] = functions
        return processed_class
    
    def __extract_function(self, node: dict[str, Any]) -> dict[str, Any]:
        functions = []
    
        # Nested functions
        for item in node.get('body', []):
            if item.get('node_type') == 'FunctionDef':
                functions.append(self.__extract_function(item))
    
        processed_function = {
            'name': node.get('name'),
            'type': 'function'
        }
        if functions:
            processed_function['functions'] = functions
        return processed_function
    
    def __init__(self, root_path: str | Path):
        self.project_tree = self.__build_project_tree(root_path)
    
    # PUBLIC METHOD
    def get_project_tree(self) -> dict[str, Any]:
        return self.project_tree
    
    @staticmethod
    def __find_node_bfs(project_tree: dict[str, Any], name: str) -> dict[str, Any]:
        if not name or name == '.' or not project_tree:
            return project_tree
        
        queue = [project_tree]
        
        while queue:
            node = queue.pop(0)
            if node.get('name', '') == name:
                return node
            for child_type in ['children', 'classes', 'functions']:
                queue.extend(node.get(child_type, []))
        
        return {}
    
    def __find_node_with_extra_info_on_failure(self, name_stack: list[str] | str) -> dict[str, Any]:
        if isinstance(name_stack, str):
            name_stack = [name_stack]
            
        found = []
        crt_node = self.get_project_tree()
        
        for name in name_stack:
            next_node = self.__find_node_bfs(crt_node, name)
            if next_node:
                found.append(name)
                crt_node = next_node
            else:
                return {
                    'error_type': 'warning',
                    'error_message': f'Couldn\'t find one of the named structures.',
                    'structure_not_found': name,
                    'structures_found': found,
                    'parsed_structure': crt_node
                }
    
        return crt_node
    
    # PUBLIC METHOD
    def find_node(self, name_stack: list[str] | str) -> dict[str, Any]:
        if isinstance(name_stack, str):
            name_stack = [name_stack]

        crt_node = self.get_project_tree()

        for name in name_stack:
            crt_node = self.__find_node_bfs(crt_node, name)

        return crt_node
