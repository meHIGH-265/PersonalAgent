from langchain_core.tools import tool, BaseTool
import requests

from Utils.CustomLogging import log
from Utils.EnvironmentVariableManager import get_default_tool_host, get_default_tool_port


host = get_default_tool_host()
port = get_default_tool_port()


def set_tool_host(tool_host: str | None = None) -> None:
    global host
    if tool_host is None:
        host = get_default_tool_host()
    else:
        host = tool_host


def set_tool_port(tool_port: int | None = None) -> None:
    global port
    if tool_port is None:
        port = get_default_tool_port()
    else:
        port = tool_port


def send_post_request_for_tool(tool_name: str, json_data: dict[str, str]) -> str:
    """
    Sends a post request to the tool endpoint
    and logs this tool usage
    """

    log_string = f'[ TOOLS ]: The {tool_name} tool has been called with parameters:'
    for parameter_name, parameter in json_data.items():
        if '\n' in parameter:
            log_string += f'\n           {parameter_name}:\n\n{parameter}\n'
        else:
            log_string += f'\n           {parameter_name}: {parameter}'
    log(log_string)

    json_data['tool_name'] = tool_name

    try:
        url = f'http://{host}:{port}/call_tool'
        headers = { 'Content-Type': 'application/json' }
        response = requests.post(url, json=json_data, headers=headers)
        return response.text
    except Exception as _:
        return f'Tool is unuseable for the moment!\nReport this issue back to the user!'


@tool
def create_file(file_path: str) -> str:
    """
    Creates an empty file.
    file_path: the relative path of the file.
    returns: a message representing the success or failure of the file creation.
    """

    json_data = {
        'file_path': file_path
    }
    return send_post_request_for_tool('create_file', json_data)


@tool
def list_files(folder_path: str = '.') -> str:
    """
    Returns the list of files and directories at the specified path.
    folder_path: the relative path of the folder to search in.
    If folder_path is one of '', '.', './', this function will return by default the list of files in the Working Directory.
    If the result is an empty list it means the folder is empty, not that the tool failed.
    """

    json_data = {
        'folder_path': folder_path
    }
    return send_post_request_for_tool('list_files', json_data)


@tool
def read_file_content(file_path: str) -> str:
    """
    Opens a file and returns its content.
    file_path: the relative path of the file
    returns: the content of the file
    """

    json_data = {
        'file_path': file_path
    }
    return send_post_request_for_tool('read_file_content', json_data)


@tool
def run_python_script(file_path: str) -> str:
    """
    Runs a python script and returns it's output.
    file_path: the relative path of the python file.
    returns: the output of the python script (it can sometimes be an error) or a message that the file didn't run.
    """

    json_data = {
        'file_path': file_path
    }
    return send_post_request_for_tool('run_python_script', json_data)


@tool
def write_in_file(file_path: str, content: str) -> str:
    """
    Overrides the content of a file (does not append!).
    file_path: the relative path of the file.
    content: the new content of the file.
    returns: a message representing the success or failure of the file writing.
    """

    json_data = {
        'file_path': file_path,
        'content': content
    }
    return send_post_request_for_tool('write_in_file', json_data)


tools = {
    'create_file': create_file,
    'list_files': list_files,
    'read_file_content': read_file_content,
    'run_python_script': run_python_script,
    'write_in_file': write_in_file
}


def get_base_tools_by_name(names: list[str] | None = None) -> dict[str, BaseTool]:
    if names is None:
        return tools
    return {the_name: the_tool for the_name, the_tool in tools.items() if the_name in names}


def main():
    print(f'{__file__} is running...')


if __name__ == '__main__':
    main()
