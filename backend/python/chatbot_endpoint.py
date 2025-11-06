from flask import Flask, request, jsonify
from flask_cors import CORS
import sys

from Services import answer_query, clear_history
from Tools.BaseTools import set_tool_host, set_tool_port
from Utils.CustomLogging import set_console_logging, set_file_logging, set_log_file
from Utils.EnvironmentVariableManager import get_default_host, get_default_port, get_default_tool_host, get_default_tool_port
from Utils.LogFileGenerator import create_nested_timestamped_log_file


app = Flask(__name__)
CORS(app)


@app.route('/chat/answer_query', methods=['POST'])
def answer_query_endpoint():
    """
    query - the user message
    streaming_host and streaming_port - unique identifiers for all users.
                                        The address to stream back the answer as it is generated
    All fields are required !
    """
    try:
        data = request.get_json()
        print(data)
        if not data or 'query' not in data or 'streaming_host' not in data or 'streaming_port' not in data:
            error_message = 'Invalid input: "query", "streaming_host" and "streaming_port" fields are all required'
            return jsonify({'error': error_message}), 400

        query = f'{data['query']}'
        streaming_host = f'{data['streaming_host']}'
        streaming_port = f'{data['streaming_port']}'

        try:
            streaming_port = int(streaming_port)
        except ValueError | TypeError:
            error_message = 'Invalid input: "streaming_port" must be an integer'
            return jsonify({'error': error_message}), 400

        print(query)
        print(streaming_host)
        print(streaming_port)

        response = answer_query(query, streaming_host, streaming_port)

        return jsonify({'response': response}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/chat/clear_history', methods=['POST'])
def clear_history_endpoint():
    """
    streaming_host and streaming_port - unique identifiers for all users.
    All fields are required !
    """
    try:
        data = request.get_json()
        print(data)
        if not data or 'streaming_host' not in data or 'streaming_port' not in data:
            err_msg = 'Invalid input: "streaming_host" and "streaming_port" fields are both required'
            return jsonify({'error': err_msg}), 400

        streaming_host = f'{data['streaming_host']}'
        streaming_port = f'{data['streaming_port']}'

        try:
            streaming_port = int(streaming_port)
        except ValueError | TypeError:
            error_message = 'Invalid input: "streaming_port" must be an integer'
            return jsonify({'error': error_message}), 400

        response = str(clear_history(streaming_host, streaming_port))

        return jsonify({'response': response}), 200
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


#   this script should be run with arguments as follows
#   python ./chatbot_endpoint.py "host" "port" "tool_host" "tool_port"
def main():
    """
    Main method that runs the endpoint at the address specified in the system variables
    And also sets the address for the tool fetches with set_tool_host() and set_tool_port()
    """
    args = sys.argv
    host = args[1] if len(args) > 1 else get_default_host()
    port = int(args[2]) if len(args) > 2 else get_default_port()
    tool_host = args[3] if len(args) > 3 else get_default_tool_host()
    tool_port = int(args[4]) if len(args) > 4 else get_default_tool_port()

    set_tool_host(tool_host)
    set_tool_port(tool_port)

    set_console_logging(True)
    set_file_logging(True)
    set_log_file(create_nested_timestamped_log_file())

    app.run(host=host, port=port, debug=False)


if __name__ == '__main__':
    main()
