var socket;

if ("WebSocket" in window) {
	console.log('Web socket supported');
	socket = createSocket();
	init();
} else {
	console.log('Web socket not supported :(');
}

document.onkeydown = function(e) {
    if (e.keyCode == 32) {
    	testDrawLine();
    }
};

