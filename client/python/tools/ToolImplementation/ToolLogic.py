import autopep8
import os
import re
import subprocess
from typing import Callable

from ToolImplementation.PythonAstParser import PythonAstParser


class ToolLogic:
    @staticmethod
    def get_default_base_directory_path() -> str:
        return '..\\..\\..\\Output'

    def __init__(self):
        self.base_directory_path: str = self.get_default_base_directory_path()

        self.tools: dict[str, Callable[[dict[str, str]], str]] = {
            'list_files': self.list_files,
            'read_file_content': self.read_file_content,
            'create_file': self.create_file,
            'write_in_file': self.write_in_file,
            'run_python_script': self.run_python_script,
            'get_file_content_structure': self.get_file_content_structure,
            'get_code_section_from_file': self.get_code_section_from_file,
            'replace_code_section_from_file': self.replace_code_section_from_file
        }

    def set_base_directory_path(self, base_directory_path: str | None = None) -> None:
        self.base_directory_path = base_directory_path
        if self.base_directory_path is None:
            self.base_directory_path = self.get_default_base_directory_path()

    def read_file_content_template(self, file_path: str) -> tuple[str, bool]:
        file_absolute_path = os.path.join(self.base_directory_path, file_path)

        if not os.path.exists(file_absolute_path):
            return f'File {file_path} doesn\'t exists!', False

        try:
            with open(file_absolute_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except OSError:
            return f'Couldn\'t read file {file_path}!', False

        return content, True

    # TOOLS

    def list_files(self, data: dict[str, str]) -> str:
        folder_path: str = data['folder_path']

        if folder_path == '.':
            folder_absolute_path = self.base_directory_path
        else:
            folder_absolute_path = os.path.join(self.base_directory_path, folder_path)

        try:
            files = os.listdir(folder_absolute_path)
        except Exception as _:
            return f'Couldn\'t open folder {folder_path}!'

        return f'{files}'

    def read_file_content(self, data: dict[str, str]) -> str:
        file_path: str = data['file_path']

        content, _ = self.read_file_content_template(file_path)
        return content

    def create_file(self, data: dict[str, str]) -> str:
        file_path: str = data['file_path']

        file_absolute_path = os.path.join(self.base_directory_path, file_path)

        if os.path.exists(file_absolute_path):
            return f'File {file_path} already exists (it\'s content was not modified by this tool call)!'

        dir_path = os.path.dirname(file_absolute_path)
        os.makedirs(dir_path, exist_ok=True)

        try:
            with open(file_absolute_path, 'w', encoding='utf-8') as file:
                file.write('def main():\n\tprint(f\'{__file__} is running...\')\n\n\nif __name__ == \'__main__\':\n\tmain()\n')

            return f'File {file_path} was successfully created!'
        except Exception as _:
            return f'Couldn\'t create file {file_path}!'

    def write_in_file(self, data: dict[str, str]) -> str:
        file_path: str = data['file_path']
        content: str = data['content']

        file_absolute_path = os.path.join(self.base_directory_path, file_path)

        if not os.path.exists(file_absolute_path):
            return f'File {file_path} does not exists!'

        if file_path.split('.')[-1] == 'py':
            content = autopep8.fix_code(content)

        try:
            with open(file_absolute_path, 'w', encoding='utf-8') as file:
                file.write(content)
            return f'Content successfully written in the file {file_path}!'
        except OSError as _:
            return f'Failed to open file {file_path}!'
        except Exception as _:
            return f'Failed to write content in the file {file_path}!'

    def run_python_script(self, data: dict[str, str]) -> str:
        file_path: str = data['file_path']

        file_absolute_path = os.path.join(self.base_directory_path, file_path)

        if not os.path.exists(file_absolute_path):
            return f'File {file_path} doesn\'t exists!'

        if file_path.split('.')[-1] != 'py':
            return f'File {file_path} is not a python file!'

        def file_to_module(file: str) -> str:
            module = file

            # if file separator is '\'
            module = module.replace('\\', '.')
            # if file separator is '/'
            module = module.replace('/', '.')

            # get rid of '.py'
            if module[-3:] == '.py':
                module = module[:-3]

            return module

        module_path = file_to_module(file_path)

        # Start with the base directory
        current_working_directory = self.base_directory_path

        # Attempt to run recursively by peeling off module parts if ModuleNotFoundError occurs
        while module_path:
            try:
                result = subprocess.run(
                    ['python', '-m', module_path],
                    cwd=current_working_directory,
                    capture_output=True,
                    text=True,
                    check=True
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
                    current_working_directory = os.path.join(current_working_directory, parts[0])
                    module_path = parts[1]

                else:
                    # Other subprocess errors, stop
                    return f'Error raised inside the script: "{e.stderr}"'

            except Exception:
                return f'Couldn\'t run script {file_path}!'

        return f'Couldn\'t resolve module for script {file_path}!'

    def get_file_content_structure(self, data: dict[str, str]) -> str:
        file_path: str = data['file_path']

        content, OK = self.read_file_content_template(file_path)
        if not OK:
            return content

        def leading_whitespace(s: str) -> str:
            i = 0
            while i < len(s) and s[i] in (" ", "\t"):
                i += 1
            return s[:i]

        summary = ''
        non_empty_lines = [line for line in content.split('\n') if line]
        for line in non_empty_lines:
            line_words = [word for word in re.split(r'\W+', line) if word]
            if not line_words:
                continue
            if line_words[0] == 'class':
                summary += f'{leading_whitespace(line)}class {line_words[1]}:\n'
            elif line_words[0] == 'def':
                summary += f'{leading_whitespace(line)}def {line_words[1]}():\n'
        return summary

    def get_code_section_from_file(self, data: dict[str, str]) -> str:
        file_path: str = data['file_path']
        section_name: str = data['section_name']

        content, OK = self.read_file_content_template(file_path)
        if not OK:
            return content

        python_ast_parser = PythonAstParser()
        return python_ast_parser.get_source_code_for_section_by_name(content, section_name)

    def replace_code_section_from_file(self, data: dict[str, str]) -> str:
        file_path: str = data['file_path']
        section_name: str = data['section_name']
        replacement: str = data['replacement']

        content, OK = self.read_file_content_template(file_path)
        if not OK:
            return content

        python_ast_parser = PythonAstParser()
        new_content = python_ast_parser.replace_section_by_name(content, section_name, replacement)
        if new_content == content:
            return f'The section with name "{section_name}" wasn\'t found. The content of the file was not modified.'

        file_absolute_path = os.path.join(self.base_directory_path, file_path)

        try:
            with open(file_absolute_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            return f'File modified successfully!'
        except OSError as _:
            return f'Failed to open file {file_path}!'
        except Exception as _:
            return f'Failed to open file {file_path}!'

    # TOOL CALLING

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
