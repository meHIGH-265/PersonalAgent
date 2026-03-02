const env = require('../env/env');

const backend_host = env.backend_host;
const backend_port = env.backend_port;

const sendUserMessage = async (query, host, port) => {
	try {
		const response = await fetch(`http://${backend_host}:${backend_port}/agents/answer_query`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ query: query, streaming_host: host, streaming_port: port }),
		});
		const json = await response.json();
		return json.response ?? json.error ?? 'Unknown response';
	} catch (err) {
		return 'Error contacting agent backend.';
	}
};

const clearHistory = async (host, port) => {
	try {
		const response = await fetch(`http://${backend_host}:${backend_port}/agents/clear_history`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ streaming_host: host, streaming_port: port }),
		});
		const json = await response.json();
		return json.response ?? json.error ?? 'Unknown response';
	} catch (err) {
		return 'Error contacting agent backend.';
	}
};

module.exports = {
    sendUserMessage,
    clearHistory
}
