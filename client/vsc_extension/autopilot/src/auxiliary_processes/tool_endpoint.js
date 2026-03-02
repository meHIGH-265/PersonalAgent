const { spawn } = require('child_process');
const path = require('path');

let flaskToolPid = null;

function startFlaskToolEndpoint(vscode, tool_endpoint_path, tool_host, tool_port) {
	const tool_path = path.resolve(__dirname, tool_endpoint_path);
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

module.exports = {
	startFlaskToolEndpoint,
	killFlaskToolProcess
}
