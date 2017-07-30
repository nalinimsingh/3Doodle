// Setup data socket
// var socket = new io.Socket('localhost',{
// 	port: 8080
// });

// socket.on('connect',function() {
// 	console.log('Client has connected to the server!');
// });

// socket.on('message',function(data) {
// 	console.log('Received a message from the server!', data);
// });

// socket.on('disconnect',function() {
// 	console.log('The client has disconnected!');
// });

// socket.connect();


var socket = new WebSocket('ws://localhost:8080');
socket.onopen = function(event) {
	console.log('Socket open');

	socket.onmessage = function(event) {
		console.log('Client received a message', event);
	};
	
	socket.onclose = function(event) {
		console.log('Socket closed');
	};
}

// Drawing initialization
init();
testDrawLine();
