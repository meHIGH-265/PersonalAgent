from flask import Flask, jsonify, request
from flask_cors import CORS
import sys

from src.Agents.AgentManager import AgentManager
from src.Agents.Tools.ToolExecutor import RemoteToolExecutor
from src.Agents.Tools.ToolManager import ToolManager
from src.Logging.CustomLogging import MixedLogger
from src.Logging.LogFileGenerator import LogFileGenerator, TimestampedLogFileGenerator
from src.Services.SingleAgentServices import SingleAgentServices
from src.Streaming.Streamer import Streamer

log_file_generator: LogFileGenerator = TimestampedLogFileGenerator('src\\Logging', 'log.txt')
logger: MixedLogger = MixedLogger(log_file_generator, separator='-_' * 50 + '-')
tool_executor: RemoteToolExecutor = RemoteToolExecutor(logger)
tool_manager: ToolManager = ToolManager(tool_folder='src\\Agents\\Tools\\Tools')
agent_manager: AgentManager = AgentManager(logger, tool_executor, tool_manager, agent_folder='src\\Agents\\Agents')
streamer: Streamer = Streamer()
services: SingleAgentServices = SingleAgentServices(agent_manager, streamer)


app = Flask(__name__)
CORS(app)


@app.route('/agents/get_all', methods=['GET'])
def get_all_agents_endpoint():
    """
    ping :)
    """
    try:
        return jsonify({'agents': agent_manager.get_agent_names()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/agents/answer_query', methods=['POST'])
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

        agent_id = f'{data['agent_id']}' if 'agent_id' in data else None

        try:
            streaming_port = int(streaming_port)
        except ValueError | TypeError:
            error_message = 'Invalid input: "streaming_port" must be an integer'
            return jsonify({'error': error_message}), 400

        print(query)
        print(streaming_host)
        print(streaming_port)

        services.call_agent(query, agent_id, streaming_host, streaming_port)

        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/agents/clear_history', methods=['POST'])
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

        response = str(services.clear_history(streaming_host, streaming_port))

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

    host = args[1] if len(args) > 1 else '127.0.0.1'
    port = int(args[2]) if len(args) > 2 else 5001

    tool_host = args[3] if len(args) > 3 else '127.0.0.1'
    tool_port = int(args[4]) if len(args) > 4 else 7001

    console_logging = bool(args[5]) if len(args) > 5 else True
    file_logging = bool(args[6]) if len(args) > 6 else True

    tool_executor.set_tool_host(tool_host)
    tool_executor.set_tool_port(tool_port)

    logger.set_console_logging(console_logging)
    logger.set_file_logging(file_logging)

    app.run(host=host, port=port, debug=False)


if __name__ == '__main__':
    main()
