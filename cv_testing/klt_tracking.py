import sys
import os

sys.path.append("/usr/local/lib/python2.7/site-packages/") 

import numpy as np
import cv2

dir = os.path.dirname(__file__)
path = os.path.join(dir,'../mock/green_pen_manual/trial2')
images = [os.path.join(path,f) for f in os.listdir(path) if not f.startswith('.')]

feature_params = dict( maxCorners = 100,
                       qualityLevel = 0.1,
                       minDistance = 7,
                       blockSize = 7 )

lk_params = dict( winSize  = (15,15),
                  maxLevel = 0,
                  criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

# Find initial features
old_frame = np.asarray(cv2.imread(images[0]))
old_frame_green = old_frame
old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
p0 = cv2.goodFeaturesToTrack(old_gray, mask = None, **feature_params)

for img in images[1:]:
    frame = np.asarray(cv2.imread(img))
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Calculate optical flow
    p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)

    # Select good points
    good_new = p1[st==1]

    # Plot features
    markers = np.zeros_like(frame_gray)
    for point in good_new:
        cv2.circle(frame, tuple(point), 5, (0,0,255), 2)

    # Show current frame    
    cv2.imshow('frame',frame)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

    old_gray = frame_gray.copy()
    p0 = good_new.reshape(-1,1,2)

cv2.destroyAllWindows()
