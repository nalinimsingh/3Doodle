init();

document.onkeydown = function(e) {
	// Space bar toggles between tracking and not tracking
    if (e.keyCode == 32) {
    	toggleTracking();
    }

    // Delete key clears canvas and stops tracking
    if (e.keyCode == 8) {
    	clearCanvas();
    	if (tracking) {
    		toggleTracking();
    	}
    }
};

