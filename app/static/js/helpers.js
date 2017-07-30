var scene, camera, renderer;
var geometry, material, line;
var tracking;
var socket;

/* Create web socket for listening to point data */
function createSocket() {
	var socket = new WebSocket('ws://localhost:5000/ws');

	socket.onerror = function(event) {
		console.log('ERROR!');
	}

	socket.onopen = function(event) {
		console.log('Socket open');
	};

	socket.onmessage = function(event) {
		console.log('Client received a message', event.data);
		var point = JSON.parse(event.data);
		addPoint(point.x, point.y, point.z);
	};

	socket.onclose = function(event) {
		console.log('Socket closed');
	};

	return socket;
}

/* Initialize drawing board */
function init(initX=0, initY=0, initZ=100, fov=50, near=1, far=500, color=0xff0000) {
	// initialize scene
	scene = new THREE.Scene();
	scene.background = new THREE.Color(0xffffff);

	// initialize camera
	camera = new THREE.PerspectiveCamera(fov, window.innerWidth / window.innerHeight, near, far);
	camera.position.set(initX, initY, initZ);
	camera.lookAt(new THREE.Vector3(0, 0, 0));

	// initialize renderer
	renderer = new THREE.WebGLRenderer(preserveDrawingBuffer=true);
	renderer.setSize(window.innerWidth, window.innerHeight);
	document.body.appendChild(renderer.domElement);

	// add line object to scene
	material = new THREE.LineBasicMaterial({color: color});
	geometry = new THREE.Geometry();
	line = new THREE.Line(geometry, material);
	scene.add(line);

	// render initial canvas
	renderer.render(scene, camera);
	tracking = false;
}

/* Toggle between starting and stopping tracking */
function toggleTracking() {
	if (tracking) {
		stopTracking();
		tracking = false;
		console.log("Tracking off");
	} else {
		startTracking();
		tracking = true;
		console.log("Tracking on");
	}
}

/* Restart drawing tracked points */
function startTracking() {
	geometry = new THREE.Geometry();
	line = new THREE.Line(geometry, material);
	scene.add(line);
	socket = createSocket();
	// TODO: make it not connect next point to previous point
}

/* Stop drawing tracked points */ 
function stopTracking() {
	socket.close();
}

/* Remove last point from drawing */
function undoPoint() {
	// create new geometry without last point
	var newVertices = geometry.vertices;
	newVertices.splice(newVertices.length-1, 1);
	clearCanvas();
	geometry.vertices = newVertices;

	// create new line and add to scene
	var newLine = new THREE.Line(geometry, material);
	scene.remove(line);
	scene.add(newLine);
	line = newLine;

	// render new scene
	renderer.render(scene, camera);
}

/* Adds a connected point to the current drawing */
function addPoint(x, y, z) {
	// create new geometry
	var newVertices = geometry.vertices;
	newVertices.push(new THREE.Vector3(x, y, z));
	geometry = new THREE.Geometry();
	geometry.vertices = newVertices;

	// create new line and add to scene
	var newLine = new THREE.Line(geometry, material);
	scene.remove(line);
	scene.add(newLine);

	// render new scene
	renderer.render(scene, camera);
}

/* Clear canvas */
function clearCanvas() {
	while(scene.children.length > 0) { 
    	scene.remove(scene.children[0]);
	}
	geometry.vertices = [];
	renderer.render(scene, camera);
}


/* Testing functions */ 
function testDrawLine() {
	addPoint(0,0,0);
	addPoint(10,0,0);
	addPoint(0,10,0);
	addPoint(15,20,0);
}

function testDisjointLines(x,y,z) {
	var firstGeometry = new THREE.Geometry();
	firstGeometry.vertices.push(new THREE.Vector3(x,y,z));
	firstGeometry.vertices.push(new THREE.Vector3(x+10,y,z));
	scene.add(new THREE.Line(firstGeometry, material));
	renderer.render(scene, camera);
}