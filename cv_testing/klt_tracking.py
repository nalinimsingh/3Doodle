import sys
import os
import time

sys.path.append("/usr/local/lib/python2.7/site-packages/") 

import numpy as np
import cv2

dir = os.path.dirname(__file__)
path = os.path.join(dir,'../mock/green_pen_manual/trial2')
images = [os.path.join(path,f) for f in os.listdir(path) if not f.startswith('.')]

feature_params = dict( maxCorners = 100,
                       qualityLevel = 0.00001,
                       minDistance = 3,
                       blockSize = 7 )

lk_params = dict( winSize  = (3,3),
                  maxLevel = 10,
                  criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 150, 0.03))

# Find initial features
old_frame = np.asarray(cv2.imread(images[0]))
mask = np.all([old_frame[:,:,0]<100,old_frame[:,:,1]>100,old_frame[:,:,2]<100],axis=0)
old_masked = old_frame*mask[:,:,np.newaxis] 
old_gray = cv2.cvtColor(old_masked, cv2.COLOR_BGR2GRAY)

# Find initial features
p0 = cv2.goodFeaturesToTrack(old_gray, mask = None, **feature_params)

# Plot features
markers = np.zeros_like(old_gray)
for point in p0:
  print point
  cv2.circle(old_masked, tuple(point[0]), 5, (0,0,255), 2)  

for img in images[1:]:
    frame = np.asarray(cv2.imread(img))
    mask = np.all([frame[:,:,0]<100,frame[:,:,1]>100,frame[:,:,2]<100],axis=0)
    frame_masked = frame*mask[:,:,np.newaxis]
    frame_gray = cv2.cvtColor(frame_masked, cv2.COLOR_BGR2GRAY)

    # Calculate optical flow
    p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)

    # Select good points
    good_new = p1[st==1]

    # Plot features
    markers = np.zeros_like(frame_gray)
    for point in good_new:
        cv2.circle(frame_masked, tuple(point), 5, (0,0,255), 2)

    # Show current frame    
    cv2.imshow('frame',cv2.resize(frame_masked, (0,0), fx=0.5, fy=0.5))
    time.sleep(0.5)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

    old_gray = frame_gray.copy()
    p0 = good_new.reshape(-1,1,2)

cv2.destroyAllWindows()

