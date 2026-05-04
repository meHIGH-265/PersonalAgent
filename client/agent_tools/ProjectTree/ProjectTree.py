from pathlib import Path
from pathspec import PathSpec
from typing import Any

from PythonAstParser.PythonAstParser import PythonAstParser


class ProjectTree:
    def __build_project_tree(self, root_path: Path | str) -> dict[str, Any]:
        """
        root_path: directory to scan
        parse_file_to_dict: function(path:str) -> structured AST dict
        """
        root: Path = Path(root_path).resolve()
        return self.__process_directory(root)

    @staticmethod
    def __is_ignored(gitignore_paths: list[Path], target_dir: Path) -> bool:
        """
        Determine if a directory should be ignored based on nested .gitignore files.

        Args:
            gitignore_paths: List of absolute Paths to .gitignore files
            target_dir: Absolute Path to the directory to check

        Returns:
            True if ignored, False otherwise
        """
        if not target_dir.is_absolute():
            raise ValueError("target_dir must be absolute")

        # Sort gitignore files by directory depth (root first)
        gitignore_paths: list[Path] = sorted(gitignore_paths, key=lambda p: len(p.parts))

        ignored: bool = False

        for gitignore in gitignore_paths:
            base_dir: Path = gitignore.parent

            # Only apply if target_dir is inside this gitignore's scope
            try:
                rel_path: Path = target_dir.relative_to(base_dir)
            except ValueError:
                continue  # not in this subtree

            if not gitignore.is_file():
                continue

            with gitignore.open("r") as f:
                lines: list[str] = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.strip().startswith("#")
                ]

            spec = PathSpec.from_lines("gitwildmatch", lines)

            # Convert to POSIX-style relative path
            rel_str: str = rel_path.as_posix()

            # Important: match_file returns True if matched by ANY rule,
            # but we need to respect negations → so we must evaluate manually
            for pattern in spec.patterns:
                if pattern.match_file(rel_str):
                    ignored = pattern.include  # include=False → ignore, True → re-include

        return ignored

    def __process_directory(self, path: Path) -> dict[str, Any]:
        if ProjectTree.__is_ignored(self.gitignore_paths, path):
            return {
                'name': path.name,
                'type': 'directory'
            }

        children: list[dict[str, Any]] = []
    
        for child in sorted(path.iterdir(), key=lambda p: (not p.is_file(), p.name)):
            if child.is_dir():
                children.append(self.__process_directory(child))
    
            elif child.suffix == '.py':
                children.append(ProjectTree.__process_python_file(child))
    
            else:
                children.append(self.__process_non_python_file(child))
    
        return {
            'name': path.name,
            'type': 'directory',
            'children': children
        }
    
    def __process_non_python_file(self, path: Path) -> dict[str, Any]:
        if path.name == '.gitignore':
            self.gitignore_paths.append(path)
        return {
            'name': path.name,
            'type': 'file'
        }

    @staticmethod
    def __process_python_file(path: Path) -> dict[str, Any]:
        with open(path, 'r', encoding='utf-8') as python_file:
            content = python_file.read()
    
        classes: list[dict[str, Any]] = []
        functions: list[dict[str, Any]] = []
    
        for node in PythonAstParser(content).parsed_python_source.get('body', []):
            node_type = node.get('node_type')
    
            if node_type == 'ClassDef':
                classes.append(ProjectTree.__extract_class(node))
    
            elif node_type == 'FunctionDef':
                functions.append(ProjectTree.__extract_function(node))
    
        processed_file: dict[str, Any] = {
            'name': path.name,
            'type': 'python_file'
        }
        if classes:
            processed_file['classes'] = classes
        if functions:
            processed_file['functions'] = functions
        return processed_file

    @staticmethod
    def __extract_class(node: dict[str, Any]) -> dict[str, Any]:
        bases: list[str] = [base.get('id') if base.get('node_type') == 'Name' else base.get('source') for base in node.get('bases', [])]
        classes: list[dict[str, Any]] = []
        functions: list[dict[str, Any]] = []

        for item in node.get('body', []):
            node_type = item.get('node_type')
    
            if node_type == 'ClassDef':
                classes.append(ProjectTree.__extract_class(item))
    
            elif node_type == 'FunctionDef':
                functions.append(ProjectTree.__extract_function(item))
    
        processed_class: dict[str, Any] = {
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

    @staticmethod
    def __extract_function(node: dict[str, Any]) -> dict[str, Any]:
        functions: list[dict[str, Any]] = []
    
        # Nested functions
        for item in node.get('body', []):
            if item.get('node_type') == 'FunctionDef':
                functions.append(ProjectTree.__extract_function(item))
    
        processed_function: dict[str, Any] = {
            'name': node.get('name'),
            'type': 'function'
        }
        if functions:
            processed_function['functions'] = functions
        return processed_function
    
    def __init__(self, root_path: Path | str):
        self.root_path: Path = Path(root_path)
        self.gitignore_paths: list[Path] = []
        self.project_tree: dict[str, Any] = self.__build_project_tree(self.root_path)
    
    def get_project_tree(self) -> dict[str, Any]:
        return self.project_tree

    @staticmethod
    def __find_node_bfs(project_tree: dict[str, Any], name: str) -> dict[str, Any]:
        if not name or name == '.' or not project_tree:
            return project_tree

        def name_match(node_name: str, searched_name: str) -> bool:
            if node_name == searched_name or (node_name.endswith('.py') and node_name[:-3] == searched_name):
                return True
            return False
        
        queue: list[dict[str, Any]] = [project_tree]
        
        while queue:
            node: dict[str, Any] = queue.pop(0)
            if name_match(node.get('name', ''), name):
                return node
            for child_type in ['children', 'classes', 'functions']:
                queue.extend(node.get(child_type, []))
        
        return {}

    def find_node(self, name_stack: list[str] | str) -> dict[str, Any]:
        if isinstance(name_stack, str):
            name_stack = [name_stack]

        crt_node: dict[str, Any] = self.get_project_tree()

        for name in name_stack:
            crt_node = ProjectTree.__find_node_bfs(crt_node, name)

        return crt_node
