import autopep8
import json
from pathlib import Path
import re
import sys
import shutil
import subprocess
from typing import Callable

from ToolImplementation.ProjectTree import ProjectTree
from ToolImplementation.PythonAstParser import PythonAstParser


class ToolLogic:
    @staticmethod
    def get_default_base_directory_path() -> Path:
        return Path('..\\..\\..\\Output')

    @staticmethod
    def compose_error_message(error_type: str, error_message: str) -> str:
        return json.dumps({
            'error_type': error_type,
            'error_message': error_message
        }, indent=2)

    def __init__(self):
        self.base_directory_path: Path = self.get_default_base_directory_path()

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

    def set_base_directory_path(self, base_directory_path: str | None = None) -> None:
        if base_directory_path is None:
            self.base_directory_path = self.get_default_base_directory_path()
        else:
            self.base_directory_path = Path(base_directory_path)

    def resolve_path(self, path: str | Path) -> Path:
        absolute_path = (self.base_directory_path / path).resolve()

        if not absolute_path.is_relative_to(self.base_directory_path):
            raise ValueError(f'Path "{path}" escapes base directory.')

        return absolute_path


    ### TOOLS

    # READ

    def read_file_content(self, data: dict[str, str]) -> str:
        file_path: str = data['file_path']

        file_absolute_path = self.resolve_path(file_path)

        if not file_absolute_path.exists():
            error_type = 'warning'
            error_message = f'The file "{file_path}" does not exist.'
            return self.compose_error_message(error_type, error_message)

        if not file_absolute_path.is_file():
            error_type = 'warning'
            error_message = f'"{file_path}" is not a file.'
            return self.compose_error_message(error_type, error_message)

        file_content = file_absolute_path.read_text(encoding='utf-8')
        return file_content

    def get_code_section_from_file(self, data: dict[str, str]) -> str:
        file_path: str = data['file_path']
        section_name: str = data['section_name']

        file_absolute_path = self.resolve_path(file_path)
        name_stack = [name for name in section_name.split('.') if name]

        if not file_absolute_path.exists():
            error_type = 'warning'
            error_message = f'The file "{file_path}" does not exist.'
            return self.compose_error_message(error_type, error_message)

        if not file_absolute_path.is_file():
            error_type = 'warning'
            error_message = f'"{file_path}" is not a file.'
            return self.compose_error_message(error_type, error_message)

        if not file_path.endswith('.py'):
            error_type = 'warning'
            error_message = f'"{file_path}" is not a python file.'
            return self.compose_error_message(error_type, error_message)

        file_content = file_absolute_path.read_text(encoding='utf-8')
        return PythonAstParser(file_content).get_source_code_for_section_by_name(name_stack)

    def find_named_structure(self, data: dict[str, str]) -> str:
        structure_name: str = data['structure_name']

        project_tree = ProjectTree(self.base_directory_path)
        name_stack = structure_name.split('.')

        structure = project_tree.find_node(name_stack)

        return json.dumps(structure, indent=2)

    def search_in_files(self, data: dict[str, str]) -> str:
        pattern: str = data['pattern']
        file_extension: str | None = data.get('file_extension')

        results = []

        for path in self.base_directory_path.rglob('*'):
            if not path.is_file():
                continue

            if file_extension and not path.name.endswith(file_extension):
                continue

            try:
                content = path.read_text(encoding='utf-8')
            except Exception:
                continue  # skip unreadable files

            for i, line in enumerate(content.splitlines(), start=1):
                if pattern in line:
                    results.append({
                        "file": str(path.relative_to(self.base_directory_path)),
                        "line_number": i,
                        "line": line.strip()
                    })

        return json.dumps(results, indent=2)

    # WRITE  ( CREATE / WRITE / EDIT / DELETE / MOVE )

    def create_file(self, data: dict[str, str]) -> str:
        file_path: str = data['file_path']

        file_absolute_path = self.resolve_path(file_path)

        if file_absolute_path.exists():
            error_type = 'warning'
            error_message = f'The file "{file_path}" already exists. It\'s content was not modified by this tool call.'
            return self.compose_error_message(error_type, error_message)

        file_absolute_path.parent.mkdir(parents=True, exist_ok=True)
        file_absolute_path.touch(exist_ok=True)

        return f'The file "{file_path}" was successfully created and is now empty.'

    def write_in_file(self, data: dict[str, str]) -> str:
        file_path: str = data['file_path']
        content: str = data['content']

        file_absolute_path = self.resolve_path(file_path)
        if file_path.split('.')[-1] == 'py':
            content = autopep8.fix_code(content)

        if not file_absolute_path.exists():
            error_type = 'warning'
            error_message = f'The file "{file_path}" does not exists. It was not created by this tool call.'
            return self.compose_error_message(error_type, error_message)

        file_absolute_path.write_text(content, encoding='utf-8')

        return f'The content was successfully written in the file "{file_path}".'

    def replace_code_section_from_file(self, data: dict[str, str]) -> str:
        file_path: str = data['file_path']
        section_name: str = data['section_name']
        replacement: str = data['replacement']

        file_absolute_path = self.resolve_path(file_path)
        name_stack = [name for name in section_name.split('.') if name]

        if not file_absolute_path.exists():
            error_type = 'warning'
            error_message = f'The file "{file_path}" does not exist.'
            return self.compose_error_message(error_type, error_message)

        if not file_absolute_path.is_file():
            error_type = 'warning'
            error_message = f'"{file_path}" is not a file.'
            return self.compose_error_message(error_type, error_message)

        if not file_path.endswith('.py'):
            error_type = 'warning'
            error_message = f'"{file_path}" is not a python file.'
            return self.compose_error_message(error_type, error_message)

        file_content = file_absolute_path.read_text(encoding='utf-8')

        new_content = PythonAstParser(file_content).replace_section_by_name(name_stack, replacement)
        if not new_content or new_content == file_content:
            return f'The section with name "{section_name}" was not found. The content of the file was not modified.'

        file_absolute_path.write_text(new_content)

        return f'The content of the file "{file_path}" was successfully modified.'

    def delete_path(self, data: dict[str, str]) -> str:
        target_path: str = data['path']
        absolute_path = self.resolve_path(target_path)

        if not absolute_path.exists():
            return self.compose_error_message(
                'warning',
                f'Path "{target_path}" does not exist.'
            )

        if absolute_path.is_file():
            absolute_path.unlink()
        elif absolute_path.is_dir():
            shutil.rmtree(absolute_path)
        else:
            return self.compose_error_message(
                'warning',
                f'Path "{target_path}" is neither a file nor a directory.'
            )

        return f'Path "{target_path}" was successfully deleted.'

    def rename_path(self, data: dict[str, str]) -> str:
        source_path: str = data['source_path']
        destination_path: str = data['destination_path']

        source_absolute = self.resolve_path(source_path)
        destination_absolute = self.resolve_path(destination_path)

        if not source_absolute.exists():
            return self.compose_error_message(
                'warning',
                f'Source path "{source_path}" does not exist.'
            )

        if destination_absolute.exists():
            return self.compose_error_message(
                'warning',
                f'Destination path "{destination_path}" already exists.'
            )

        destination_absolute.parent.mkdir(parents=True, exist_ok=True)
        source_absolute.rename(destination_absolute)

        return f'"{source_path}" was successfully moved/renamed to "{destination_path}".'

    # EXECUTE / INSTALL LIBRARY

    def run_python_script(self, data: dict[str, str]) -> str:
        file_path: str = data['file_path']

        file_absolute_path = self.resolve_path(file_path)

        if not file_absolute_path.exists():
            error_type = 'warning'
            error_message = f'The file "{file_path}" does not exist.'
            return self.compose_error_message(error_type, error_message)

        if not file_absolute_path.is_file():
            error_type = 'warning'
            error_message = f'"{file_path}" is not a file.'
            return self.compose_error_message(error_type, error_message)

        if not file_path.endswith('.py'):
            error_type = 'warning'
            error_message = f'"{file_path}" is not a python file.'
            return self.compose_error_message(error_type, error_message)

        def file_to_module(file: str) -> str:
            module = file

            # if file separator is '\'
            module = module.replace('\\', '.')
            # if file separator is '/'
            module = module.replace('/', '.')

            # get rid of '.py'
            if module.endswith(',py'):
                module = module[:-3]

            return module

        module_path = file_to_module(file_path)

        # Start with the base directory
        current_working_directory = self.base_directory_path

        # Attempt to run recursively by peeling off module parts if ModuleNotFoundError occurs
        timeout_in_seconds = 5
        while module_path:
            try:
                result = subprocess.run(
                    ['python', '-m', module_path],
                    cwd=current_working_directory,
                    capture_output=True,
                    text=True,
                    check=True,
                    encoding='utf-8',
                    timeout=timeout_in_seconds
                )
                return result.stdout

            except subprocess.CalledProcessError as e:
                # Check if the error is ModuleNotFoundError
                if 'ModuleNotFoundError' in e.stderr:
                    # Peel off the first part of the module and adjust cwd
                    parts = module_path.split('.', 1)
                    if len(parts) <= 1:
                        # Nothing left to peel, give up
                        return f'Error raised inside the script: "{e.stderr}"'

                    # Move first part into cwd
                    current_working_directory = current_working_directory / parts[0]
                    module_path = parts[1]

                else:
                    # Other subprocess errors, stop
                    return f'Error raised inside the script: "{e.stderr}"'

            except subprocess.TimeoutExpired:
                return f'Script exceeded the timeout of {timeout_in_seconds} seconds.'

        return f'Couldn\'t resolve module for script {file_path}!'

    def install_package(self, data: dict[str, str]) -> str:
        package_name: str = data['package_name']
        timeout_in_seconds = 60

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package_name],
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8',
                timeout=timeout_in_seconds
            )

            return result.stdout

        except subprocess.CalledProcessError as e:
            return self.compose_error_message(
                "error",
                f"Package installation failed:\n{e.stderr}"
            )

        except subprocess.TimeoutExpired:
            return self.compose_error_message(
                "error",
                f"Installation exceeded timeout of {timeout_in_seconds} seconds."
            )

        except Exception as e:
            return self.compose_error_message("error", str(e))

    ### OLD TOOLS

    def list_files(self, data: dict[str, str]) -> str:
        folder_path: str = data['folder_path']

        folder_absolute_path = self.resolve_path(folder_path)

        if not folder_absolute_path.exists():
            error_type = 'warning'
            error_message = f'The folder "{folder_path}" does not exist.'
            return self.compose_error_message(error_type, error_message)

        if not folder_absolute_path.is_dir():
            error_type = 'warning'
            error_message = f'"{folder_path}" is not a directory.'
            return self.compose_error_message(error_type, error_message)

        return list(folder_absolute_path.iterdir()).__str__()

    def get_file_content_structure(self, data: dict[str, str]) -> str:
        file_path: str = data['file_path']

        file_absolute_path = self.resolve_path(file_path)

        if not file_absolute_path.exists():
            error_type = 'warning'
            error_message = f'The file "{file_path}" does not exist.'
            return self.compose_error_message(error_type, error_message)

        if not file_absolute_path.is_file():
            error_type = 'warning'
            error_message = f'"{file_path}" is not a file.'
            return self.compose_error_message(error_type, error_message)

        file_content = file_absolute_path.read_text(encoding='utf-8')

        def leading_whitespace(s: str) -> str:
            i = 0
            while i < len(s) and s[i] in (" ", "\t"):
                i += 1
            return s[:i]

        summary = ''
        non_empty_lines = [line for line in file_content.split('\n') if line]
        for line in non_empty_lines:
            line_words = [word for word in re.split(r'\W+', line) if word]
            if not line_words:
                continue
            if line_words[0] == 'class':
                summary += f'{leading_whitespace(line)}class {line_words[1]}:\n'
            elif line_words[0] == 'def':
                summary += f'{leading_whitespace(line)}def {line_words[1]}():\n'
        return summary

    ### TOOL CALLING

    @staticmethod
    def non_existing_tool(*args, **kwargs) -> str:
        return (
            'The tool you are looking for does not exist. '
            'Please check your spelling, and if the problem persists '
            'report back to the user.'
        )

    def handle_tool_call(self, tool_name: str, data: dict[str, str]) -> str:
        selected_tool = self.tools.get(tool_name) if tool_name in self.tools else self.non_existing_tool

        return selected_tool(data)
