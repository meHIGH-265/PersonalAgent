from flask import Flask, jsonify, request
from flask_cors import CORS
from json import dumps
from sys import argv

from ToolImplementation.ToolLogic import ToolLogic


tool_logic: ToolLogic = ToolLogic()


app = Flask(__name__)
CORS(app)


@app.route('/call_tool', methods=['POST'])
def call_tool_endpoint():
    """
    tool_name - the name of the called tool
    other keys - parameters for the called tool
    returns - the result of the tool call, a success message or a failure message
    """
    tool_name = None
    try:
        data: dict[str, str] = request.get_json()
        print(f'Tool was called: {dumps(data, indent=2)}')

        if not data or type(data) is not dict or 'tool_name' not in data:
            error_type = 'invalid input'
            error_message = '"tool_name" must be included when calling a tool.'
            return jsonify({'error': f'{error_type} -> {error_message}'}), 400

        tool_name = data['tool_name']
        return tool_logic.handle_tool_call(tool_name, data), 200

    except KeyError as e:
        error_type = 'invalid input'
        error_message = f'parameter {e} mandatory for tool {tool_name}'
        return jsonify({'error': f'{error_type} -> {error_message}'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/ping', methods=['GET'])
def ping_endpoint():
    """
    ping :)
    """
    try:
        return jsonify({'response': 'OK'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def main():
    args: list[str] = argv
    tool_host: str = args[1] if len(args) > 1 else '127.0.0.1'
    tool_port: int = int(args[2]) if len(args) > 2 else 7001
    base_directory_path: str = args[3] if len(args) > 3 else None

    tool_logic.set_base_directory_path(base_directory_path)

    app.run(host=tool_host, port=tool_port, debug=False)


if __name__ == '__main__':
    main()
