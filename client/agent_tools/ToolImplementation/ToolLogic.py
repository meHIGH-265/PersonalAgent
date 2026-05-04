from autopep8 import fix_code
from json import dumps
from pathlib import Path
from sys import executable
from shutil import rmtree
from subprocess import CalledProcessError, TimeoutExpired, run
from typing import Any, Callable

from ProjectTree.ProjectTree import ProjectTree
from PythonAstParser.PythonAstParser import PythonAstParser


class ToolLogic:
    @staticmethod
    def __get_default_base_directory_path() -> Path:
        return Path(__file__).parents[3] / 'Output'

    @staticmethod
    def __compose_error_message(error_type: str, error_message: str) -> str:
        return dumps(obj={
            'error_type': error_type,
            'error_message': error_message
        }, indent=2)

    def __init__(self):
        self.base_directory_path: Path = ToolLogic.__get_default_base_directory_path()

        self.tools: dict[str, Callable[[dict[str, str]], str]] = {
            'read_file_content': self.read_file_content,
            'get_code_section_from_file': self.get_code_section_from_file,
            'find_named_structure': self.find_named_structure,
            'search_in_files': self.search_in_files,
            'create_file': self.create_file,
            'write_in_file': self.write_in_file,
            'replace_code_section_from_file': self.replace_code_section_from_file,
            'delete_path': self.delete_path,
            'rename_path': self.rename_path,
            'run_python_script': self.run_python_script,
            'install_package': self.install_package
        }

    def set_base_directory_path(self, base_directory_path: Path | str | None = None) -> None:
        self.base_directory_path = Path(base_directory_path or ToolLogic.__get_default_base_directory_path())

    def resolve_path(self, path: Path | str) -> Path:
        absolute_path: Path = (self.base_directory_path / path).resolve()

        if not absolute_path.is_relative_to(self.base_directory_path):
            raise ValueError(f'Path "{path}" escapes base directory.')

        return absolute_path

    ### TOOLS

    # READ

    def read_file_content(self, data: dict[str, str]) -> str:
        file_path: str = data['file_path']

        file_absolute_path: Path = self.resolve_path(file_path)

        if not file_absolute_path.exists():
            error_type = 'warning'
            error_message = f'The file "{file_path}" does not exist.'
            return ToolLogic.__compose_error_message(error_type, error_message)

        if not file_absolute_path.is_file():
            error_type = 'warning'
            error_message = f'"{file_path}" is not a file.'
            return ToolLogic.__compose_error_message(error_type, error_message)

        file_content: str = file_absolute_path.read_text(encoding='utf-8')
        return file_content

    def get_code_section_from_file(self, data: dict[str, str]) -> str:
        file_path: str = data['file_path']
        section_name: str = data['section_name']

        file_absolute_path: Path = self.resolve_path(file_path)
        name_stack: list[str] = [name for name in section_name.split('.') if name]

        if not file_absolute_path.exists():
            error_type = 'warning'
            error_message = f'The file "{file_path}" does not exist.'
            return ToolLogic.__compose_error_message(error_type, error_message)

        if not file_absolute_path.is_file():
            error_type = 'warning'
            error_message = f'"{file_path}" is not a file.'
            return ToolLogic.__compose_error_message(error_type, error_message)

        if not file_path.endswith('.py'):
            error_type = 'warning'
            error_message = f'"{file_path}" is not a python file.'
            return ToolLogic.__compose_error_message(error_type, error_message)

        file_content: str = file_absolute_path.read_text(encoding='utf-8')
        return PythonAstParser(file_content).get_source_code_for_section_by_name(name_stack)

    def find_named_structure(self, data: dict[str, str]) -> str:
        structure_name: str = data['structure_name']

        project_tree: ProjectTree = ProjectTree(self.base_directory_path)
        name_stack: list[str] = structure_name.split('.')

        structure: dict[str, Any] = project_tree.find_node(name_stack)

        return dumps(structure, indent=2)

    def search_in_files(self, data: dict[str, str]) -> str:
        pattern: str = data['pattern']
        file_extension: str | None = data.get('file_extension')

        results: list[dict[str, Any]] = []

        for path in self.base_directory_path.rglob('*'):
            if not path.is_file():
                continue

            if file_extension and not path.name.endswith(file_extension):
                continue

            try:
                content: str = path.read_text(encoding='utf-8')
            except Exception:
                continue  # skip unreadable files

            for i, line in enumerate(content.splitlines(), start=1):
                if pattern in line:
                    results.append({
                        "file": str(path.relative_to(self.base_directory_path)),
                        "line_number": i,
                        "line": line.strip()
                    })

        return dumps(results, indent=2)

    # WRITE  ( CREATE / WRITE / EDIT / DELETE / MOVE )

    def create_file(self, data: dict[str, str]) -> str:
        file_path: str = data['file_path']

        file_absolute_path: Path = self.resolve_path(file_path)

        if file_absolute_path.exists():
            error_type = 'warning'
            error_message = f'The file "{file_path}" already exists. It\'s content was not modified by this tool call.'
            return ToolLogic.__compose_error_message(error_type, error_message)

        file_absolute_path.parent.mkdir(parents=True, exist_ok=True)
        file_absolute_path.touch(exist_ok=True)

        return f'The file "{file_path}" was successfully created and is now empty.'

    def write_in_file(self, data: dict[str, str]) -> str:
        file_path: str = data['file_path']
        content: str = data['content']

        file_absolute_path: Path = self.resolve_path(file_path)
        if file_path.endswith('.py'):
            content: str = fix_code(content)

        if not file_absolute_path.exists():
            error_type = 'warning'
            error_message = f'The file "{file_path}" does not exists. It was not created by this tool call.'
            return ToolLogic.__compose_error_message(error_type, error_message)

        file_absolute_path.write_text(content, encoding='utf-8')

        return f'The content was successfully written in the file "{file_path}".'

    def replace_code_section_from_file(self, data: dict[str, str]) -> str:
        file_path: str = data['file_path']
        section_name: str = data['section_name']
        replacement: str = data['replacement']

        file_absolute_path: Path = self.resolve_path(file_path)
        name_stack: list[str] = [name for name in section_name.split('.') if name]

        if not file_absolute_path.exists():
            error_type = 'warning'
            error_message = f'The file "{file_path}" does not exist.'
            return ToolLogic.__compose_error_message(error_type, error_message)

        if not file_absolute_path.is_file():
            error_type = 'warning'
            error_message = f'"{file_path}" is not a file.'
            return ToolLogic.__compose_error_message(error_type, error_message)

        if not file_path.endswith('.py'):
            error_type = 'warning'
            error_message = f'"{file_path}" is not a python file.'
            return ToolLogic.__compose_error_message(error_type, error_message)

        file_content: str = file_absolute_path.read_text(encoding='utf-8')

        new_content: str = PythonAstParser(file_content).replace_section_by_name(name_stack, replacement)
        if not new_content or new_content == file_content:
            return f'The section with name "{section_name}" was not found. The content of the file was not modified.'

        file_absolute_path.write_text(new_content, encoding='utf-8')

        return f'The content of the file "{file_path}" was successfully modified.'

    def delete_path(self, data: dict[str, str]) -> str:
        target_path: str = data['path']

        absolute_path: Path = self.resolve_path(target_path)

        if not absolute_path.exists():
            error_type = 'warning'
            error_message = f'The path "{target_path}" does not exist.'
            return ToolLogic.__compose_error_message(error_type, error_message)

        if absolute_path.is_file():
            absolute_path.unlink()
        elif absolute_path.is_dir():
            rmtree(absolute_path)
        else:
            error_type = 'warning'
            error_message = f'The path "{target_path}" is neither a file nor a directory.'
            return ToolLogic.__compose_error_message(error_type, error_message)

        return f'The path "{target_path}" was successfully deleted.'

    def rename_path(self, data: dict[str, str]) -> str:
        source_path: str = data['source_path']
        destination_path: str = data['destination_path']

        source_absolute: Path = self.resolve_path(source_path)
        destination_absolute: Path = self.resolve_path(destination_path)

        if not source_absolute.exists():
            error_type = 'warning'
            error_message = f'The source path "{source_path}" does not exist.'
            return ToolLogic.__compose_error_message(error_type, error_message)

        if destination_absolute.exists():
            error_type = 'warning'
            error_message = f'The destination path "{destination_path}" already exists.'
            return ToolLogic.__compose_error_message(error_type, error_message)

        destination_absolute.parent.mkdir(parents=True, exist_ok=True)
        source_absolute.rename(destination_absolute)

        return f'"{source_path}" was successfully moved/renamed to "{destination_path}".'

    # EXECUTE / INSTALL LIBRARY

    def run_python_script(self, data: dict[str, str]) -> str:
        file_path: str = data['file_path']

        file_absolute_path: Path = self.resolve_path(file_path)

        if not file_absolute_path.exists():
            error_type = 'warning'
            error_message = f'The file "{file_path}" does not exist.'
            return ToolLogic.__compose_error_message(error_type, error_message)

        if not file_absolute_path.is_file():
            error_type = 'warning'
            error_message = f'"{file_path}" is not a file.'
            return ToolLogic.__compose_error_message(error_type, error_message)

        if not file_path.endswith('.py'):
            error_type = 'warning'
            error_message = f'"{file_path}" is not a python file.'
            return ToolLogic.__compose_error_message(error_type, error_message)

        def file_to_module(file: str) -> str:
            module: str = file

            # if file separator is '\'
            module = module.replace('\\', '.')
            # if file separator is '/'
            module = module.replace('/', '.')

            # get rid of '.py'
            if module.endswith('.py'):
                module = module[:-3]

            return module

        module_path: str = file_to_module(file_path)

        # Start with the base directory
        current_working_directory: Path = self.base_directory_path

        # Attempt to run recursively by peeling off module parts if ModuleNotFoundError occurs
        timeout_in_seconds: int = 5
        while module_path:
            try:
                result = run(
                    args=['python', '-m', module_path],
                    cwd=current_working_directory,
                    capture_output=True,
                    text=True,
                    check=True,
                    encoding='utf-8',
                    timeout=timeout_in_seconds
                )
                return result.stdout

            except CalledProcessError as e:
                # Check if the error is ModuleNotFoundError
                if 'ModuleNotFoundError' in e.stderr:
                    # Peel off the first part of the module and adjust cwd
                    parts: list[str] = module_path.split('.', 1)
                    if len(parts) <= 1:
                        # Nothing left to peel, give up
                        return f'Error raised inside the script: "{e.stderr}"'

                    # Move first part into cwd
                    current_working_directory: Path = current_working_directory / parts[0]
                    module_path: str = parts[1]

                else:
                    # Other subprocess errors, stop
                    return f'Error raised inside the script:\n\n{e.stderr}'

            except TimeoutExpired:
                return f'Script exceeded the timeout of {timeout_in_seconds} seconds.'

        return f'Couldn\'t resolve module for script {file_path}!'

    def install_package(self, data: dict[str, str]) -> str:
        package_name: str = data['package_name']
        timeout_in_seconds: int = 60

        try:
            result = run(
                args=[executable, "-m", "pip", "install", package_name],
                cwd=self.base_directory_path,
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8',
                timeout=timeout_in_seconds
            )

            return result.stdout

        except CalledProcessError as e:
            error_type = 'warning'
            error_message = f'Package installation failed:\n{e.stderr}'
            return ToolLogic.__compose_error_message(error_type, error_message)

        except TimeoutExpired:
            error_type = 'warning'
            error_message = f'Installation exceeded timeout of {timeout_in_seconds} seconds.'
            return ToolLogic.__compose_error_message(error_type, error_message)

    ### TOOL CALLING

    @staticmethod
    def non_existing_tool(*args, **kwargs) -> str:
        return (
            'The tool you are looking for does not exist. '
            'Please check your spelling, and if the problem persists '
            'report back to the user.'
        )

    def handle_tool_call(self, tool_name: str, data: dict[str, str]) -> str:
        selected_tool: Callable[[dict[str, str]], str] = self.tools.get(tool_name, self.non_existing_tool)
        return selected_tool(data)
