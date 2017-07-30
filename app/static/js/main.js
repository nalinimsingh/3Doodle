init();
// testDrawLine();

document.onkeydown = function(e) {
	// Space bar toggles between tracking and not tracking
    if (e.keyCode === 32) {
    	toggleTracking();
    }

    // Delete key clears canvas and stops tracking
    if (e.keyCode === 8) {
    	clearCanvas();
    	if (tracking) {
    		toggleTracking();
    	}
    }

    // 'u' key undos previous point if not tracking
    if (e.keyCode === 85) {
    	console.log('Left arrow');
    	if (!tracking) {
    		undoPoint();
    	}
    }
};