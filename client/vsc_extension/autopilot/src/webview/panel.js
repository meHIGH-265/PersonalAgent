const vscode = require('vscode');
const { startSocketServer } = require('../comunication/socket_server');
const { sendUserMessage, clearHistory } = require('../comunication/chat_api');
const { getWebviewContent } = require('./get_webview_content');
const env = require('../env/env');

const createAgentPanel = (context) => {
	const panel = vscode.window.createWebviewPanel(
		'autopilot panel',
		'AI Assistant',
		vscode.ViewColumn.Beside,
		{ enableScripts: true }
	);

	const webview = panel.webview;
	const streaming_host = env.streaming_host;
	const streaming_port = env.streaming_port;

	const socketServer = startSocketServer(streaming_host, streaming_port, (data) => {
		webview.postMessage({ type: 'ai_message', message: data });
	});

	webview.onDidReceiveMessage(async (message) => {
		if (message.type === 'sendUserMessage') {
			const statusMsg = await sendUserMessage(message.query, streaming_host, streaming_port);
			webview.postMessage({ type: 'status', message: statusMsg });
		}
        else if (message.type === 'clearHistory') {
			const statusMsg = await clearHistory(streaming_host, streaming_port);
			webview.postMessage({ type: 'status', message: statusMsg });
		}
	});

	panel.onDidDispose(() => {
		socketServer.close();
	});

	webview.html = getWebviewContent(context, panel);
};

module.exports = {
    createAgentPanel
}
