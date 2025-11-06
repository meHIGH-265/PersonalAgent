// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
const vscode = require('vscode');

const path = require('path');
const { spawn } = require('child_process');
const { createAgentPanel } = require('./src/webview/panel');
const env = require('./src/env/env');

let flaskToolPid = null;

function startFlaskToolEndpoint() {
	const tool_path = path.resolve(__dirname, env.tool_path);
	const tool_host = env.tool_host;
	const tool_port = env.tool_port;
	const ai_working_space = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;	// The folder opened in the extension window
	console.log(`Opened folder: ${ai_working_space}`);

	// Start the Flask server
	const flaskProcess = spawn('python', [tool_path, tool_host, tool_port, ai_working_space], {
		detached: true,  // This allows the process to run independently
		stdio: ['ignore', 'pipe', 'pipe'],  // Capture stdout and stderr
		env: {
			...process.env, // păstrează restul variabilelor de mediu
			PYTHONIOENCODING: 'utf-8' // forțează stdout/stderr să fie UTF-8
		}  // Capture stdout and stderr
	});

	// Log standard output
	flaskProcess.stdout.on('data', (data) => {
		console.log(`From tools:\n${data.toString('utf8')}`);
	});

	// Log standard error
	flaskProcess.stderr.on('data', (data) => {
		console.error(`From tools:\n${data.toString('utf8')}`);
	});

	flaskToolPid = flaskProcess.pid;
	console.log(`Flask tool process pid: ${flaskToolPid}`);

	// Detach from parent process
	flaskProcess.unref();

	return flaskToolPid;
}

function killFlaskToolProcess() {
	if (flaskToolPid === null) { return; }
	console.log(`Killing flask tool process [${flaskToolPid}]...`);
	process.kill(flaskToolPid);
}

let flaskBackendPid = null;

function startFlaskBackendEndpoint() {
	const backend_path = path.resolve(__dirname, env.backend_path);
	const backend_host = env.backend_host;
	const backend_port = env.backend_port;
	const tool_host = env.tool_host;
	const tool_port = env.tool_port;

	// Start the Flask server
	const flaskProcess = spawn('python', [backend_path, backend_host, backend_port, tool_host, tool_port], {
		detached: true,  // This allows the process to run independently
		stdio: ['ignore', 'pipe', 'pipe'],  // Capture stdout and stderr
		env: {
			...process.env, // păstrează restul variabilelor de mediu
			PYTHONIOENCODING: 'utf-8' // forțează stdout/stderr să fie UTF-8
		}
	});

	// Log standard output
	flaskProcess.stdout.on('data', (data) => {
		console.log(`From backend:\n${data.toString('utf8')}`);
	});

	// Log standard error
	flaskProcess.stderr.on('data', (data) => {
		console.error(`From backend:\n${data.toString('utf8')}`);
	});

	flaskBackendPid = flaskProcess.pid;
	console.log(`Flask backend process pid: ${flaskBackendPid}`);

	// Detach from parent process
	flaskProcess.unref();

	return flaskBackendPid;
}

function killFlaskBackendProcess() {
	if (flaskBackendPid === null) { return; }
	console.log(`Killing flask backend process [${flaskBackendPid}]...`);
	process.kill(flaskBackendPid);
}

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
		
		startFlaskToolEndpoint();		// Starts the Tool endpoint
		startFlaskBackendEndpoint();	// Starts the Backend endpoint

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
