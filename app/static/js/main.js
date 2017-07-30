var socket;

if ("WebSocket" in window) {
	console.log('Web socket supported');
	createSocket();
	init();
	testDrawLine();
} else {
	console.log('Web socket not supported :(');
}

function createSocket() {
	socket = new WebSocket('ws://localhost:8080');

	socket.onerror = function(event) {
		console.log('ERROR!');
	}

	socket.onopen = function(event) {
		console.log('Socket open');
	};

	socket.onmessage = function(event) {
		console.log('Client received a message', event);
	};

	socket.onclose = function(event) {
		console.log('Socket closed');
	};
}