const { spawn } = require('child_process');
const path = require('path');

let flaskBackendPid = null;

function startFlaskBackendEndpoint(vscode, backend_endpoint_path, backend_host, backend_port, tool_host, tool_port) {
	const backend_path = path.resolve(__dirname, backend_endpoint_path);

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

module.exports = {
	startFlaskBackendEndpoint,
	killFlaskBackendProcess
}
