from flask import Flask, request, jsonify
from flask_cors import CORS
import sys

from tool_logic import set_ai_working_space, handle_tool_call, default_ai_working_space


default_tool_host = '127.0.0.1'
default_tool_port = 7001
app = Flask(__name__)
CORS(app)


@app.route('/call_tool', methods=['POST'])
def call_tool_endpoint():
    try:
        data: dict[str, str] = request.get_json()
        print(data)
        if not data or type(data) is not dict or 'tool_name' not in data:
            error_message = 'Invalid input: "tool_name" must be included.'
            return error_message, 400
        tool_name = data['tool_name']
        tool_response = handle_tool_call(tool_name, data)
        return tool_response, 200
    except KeyError as e:
        error_message = f'Invalid input: {e}'
        return error_message, 400
    except Exception as e:
        return str(e), 500


def main():
    args = sys.argv
    tool_host = args[1] if len(args) > 1 else default_tool_host
    tool_port = int(args[2]) if len(args) > 2 else default_tool_port
    ai_working_space = args[3] if len(args) > 3 else default_ai_working_space

    set_ai_working_space(ai_working_space)

    app.run(host=tool_host, port=tool_port, debug=False)


if __name__ == '__main__':
    main()
