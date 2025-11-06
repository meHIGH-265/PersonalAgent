const net = require('net');

const startSocketServer = (host, port, onData) => {
	const server = net.createServer((socket) => {
		socket.on('data', (data) => {
			onData(data.toString());
		});
	});

	server.listen(port, host, () => {
		console.log(`Socket server listening on ${host}:${port}`);
	});

	return server;
};

module.exports = {
    startSocketServer
}
