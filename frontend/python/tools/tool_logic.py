import autopep8
import os
import subprocess


default_ai_working_space = '../../../Output'
AI_WORKING_SPACE = default_ai_working_space


def set_ai_working_space(ai_working_space: str | None = None) -> None:
    global AI_WORKING_SPACE
    if ai_working_space is None:
        AI_WORKING_SPACE = default_ai_working_space
    else:
        AI_WORKING_SPACE = ai_working_space


def create_file(data: dict[str, str]) -> str:
    file_path = data['file_path']

    file_absolute_path = os.path.join(AI_WORKING_SPACE, file_path)

    if os.path.exists(file_absolute_path):
        return f'File {file_path} already exists (it\'s content was not modified by this tool call)!'

    dir_path = os.path.dirname(file_absolute_path)
    os.makedirs(dir_path, exist_ok=True)

    try:
        with open(file_absolute_path, 'w', encoding='utf-8') as file:
            file.write('')

        return f'File {file_path} was successfully created!'
    except Exception as _:
        return f'Failed to create file {file_path}!'


def list_files(data: dict[str, str]) -> str:
    folder_path = data['folder_path']

    if folder_path in ['', '.', './']:
        folder_absolute_path = AI_WORKING_SPACE
    else:
        folder_absolute_path = os.path.join(AI_WORKING_SPACE, folder_path)

    try:
        files = os.listdir(folder_absolute_path)
    except Exception as _:
        return f'Failed to open folder {folder_path}!'

    return f'{files}'


def read_file_content(data: dict[str, str]) -> str:
    file_path = data['file_path']

    file_absolute_path = os.path.join(AI_WORKING_SPACE, file_path)

    try:
        with open(file_absolute_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except OSError:
        content = ''

    return content


def run_python_script(data: dict[str, str]) -> str:
    file_path = data['file_path']

    file_absolute_path = os.path.join(AI_WORKING_SPACE, file_path)

    if not os.path.exists(file_absolute_path):
        return f'File {file_path} does not exists!'

    if file_path.split('.')[-1] != 'py':
        return f'File {file_path} is not a python file!'

    try:
        result = subprocess.run(["python", file_absolute_path], capture_output=True, text=True, check=True)
        output_message = f"{result.stdout}"
    except subprocess.CalledProcessError as e:
        output_message = f"Error while running the script: {e.stderr}"
    except Exception as _:
        return f'Failed to run the script {file_path}!'

    return output_message


def write_in_file(data: dict[str, str]) -> str:
    file_path = data['file_path']
    content = data['content']

    file_absolute_path = os.path.join(AI_WORKING_SPACE, file_path)

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


tools = {
    'create_file': create_file,
    'list_files': list_files,
    'read_file_content': read_file_content,
    'run_python_script': run_python_script,
    'write_in_file': write_in_file
}


def handle_tool_call(tool_name: str, data: dict[str, str]) -> str:
    tool_response = tools[tool_name](data)
    return tool_response


def main():
    print(f'{__file__} is running...')


if __name__ == '__main__':
    main()
