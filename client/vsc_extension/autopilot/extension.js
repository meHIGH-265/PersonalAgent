// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
const vscode = require('vscode');

const { createAgentPanel } = require('./src/webview/panel');
const env = require('./src/env/env');
const { startFlaskBackendEndpoint, killFlaskBackendProcess } = require('./src/auxiliary_processes/backend_endpoint')
const { startFlaskToolEndpoint, killFlaskToolProcess } = require('./src/auxiliary_processes/tool_endpoint')

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {

	// This line of code will only be executed once when your extension is activated
	console.log('Congratulations, your extension "autopilot" is now active!');

	const disposable = vscode.commands.registerCommand('autopilot.open', function () {
		// The code you place here will be executed every time your command is executed
		
		// Starts the Tool endpoint
		startFlaskToolEndpoint(vscode, env.tool_path, env.tool_host, env.tool_port);

		// Starts the Backend endpoint
		// startFlaskBackendEndpoint(vscode, env.backend_path, env.backend_host, env.backend_port, env.tool_host, env.tool_port);

		createAgentPanel(context);
	});

	context.subscriptions.push(disposable);
}

// This method is called when your extension is deactivated
function deactivate() {
	killFlaskBackendProcess();
	killFlaskToolProcess();
}

module.exports = {
	activate,
	deactivate
}
