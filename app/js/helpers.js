var scene, camera, renderer;
var geometry, material, line;

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
	// geometry.dynamic = true;
	line = new THREE.Line(geometry, material);
	scene.add(line);
}

/* Remove last point from drawing */
function undoPoint() {
	// create new geometry without last point
	var newVertices = geometry.vertices;
	newVertices.splice(newVertices.length-1, 1);
	clearCanvas();
	geometry = new THREE.Geometry();
	geometry.vertices = newVertices;

	// create new line and add to scene
	var newLine = new THREE.Line(geometry, material);
	scene.remove(line);
	scene.add(newLine);

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

/* Test line drawing function */ 
function testDrawLine(x, y, z) {
	addPoint(0,0,0);
	addPoint(10,0,0);
	addPoint(10,10,0);
	addPoint(15,20,0);
}