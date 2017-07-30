import sys
import os
import time
import numpy as np
import scipy.cluster
import cv2
import itertools

def mask_image(image):
    mask = np.all([image[:,:,0]<100,image[:,:,1]>100,image[:,:,2]<100],axis=0)
    masked_image = image*mask[:,:,np.newaxis]
    return masked_image

class KLTTracker():
    def __init__(self):
        self.xmin = 100
        self.xmax = 1650
        self.ymin = 150
        self.ymax = 1000
        self.feature_params = dict(maxCorners = 10,
                         qualityLevel = 0.00001,
                         minDistance = 5,
                         blockSize = 7 )

        self.lk_params = dict( winSize  = (5,5),
                    maxLevel = 10,
                    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 100, 0.05))

    # initial_img_array: Numpy array
    def detect_features(self,initial_img_array):
        old_frame = initial_img_array[self.ymin:self.ymax,self.xmin:self.xmax,:]
        old_masked = mask_image(old_frame)
        self.old_gray = cv2.cvtColor(old_masked, cv2.COLOR_BGR2GRAY)
        self.p0 = cv2.goodFeaturesToTrack(self.old_gray, mask = None, **self.feature_params)

    def init_feature_tracking(self):
        self.point_history = []

    def track_features(self,input_img_array):
        self.frame = input_img_array[self.ymin:self.ymax,self.xmin:self.xmax,:]
        frame_masked = mask_image(self.frame)
        self.frame_gray = cv2.cvtColor(frame_masked, cv2.COLOR_BGR2GRAY)

        # Calculate optical flow
        self.p1, st, err = cv2.calcOpticalFlowPyrLK(self.old_gray, self.frame_gray, self.p0, None, **self.lk_params)

        # Select good points
        self.good_new = self.p1[st==1]

    def cluster(self):
      clusters= scipy.cluster.hierarchy.fclusterdata(self.good_new, 1, criterion='inconsistent', metric='euclidean', depth=2, method='average', R=None)
      self.pen_tip = self.good_new[clusters == 1]

    def average(self):
        self.avg = np.average(self.pen_tip,axis=0)
        self.point_history.append(self.avg)

        for a,b in itertools.izip(self.point_history, self.point_history[1:]):
            cv2.line(self.frame, tuple(a), tuple(b), (255,0,0))

    # Prepare for the next round of tracking
    def update(self):
        self.old_gray = self.frame_gray.copy()
        self.p0 = self.good_new.reshape(-1,1,2)

    def get_frame(self):
        return self.frame

    def get_frame_gray(self):
        return self.frame_gray

    def get_good_new(self):
        return self.good_new

    def get_pen_tip(self):
        return self.pen_tip


def main():
    dir = os.path.dirname(__file__)
    path = os.path.join(dir,'../mock/green_pen_manual/trial1')
    images = [os.path.join(path,f) for f in os.listdir(path) if not f.startswith('.')]

    feature_tracker = KLTTracker()
    feature_tracker.detect_features(np.asarray(cv2.imread(images[0])))
    feature_tracker.init_feature_tracking()

    for img in images[1:]:
        feature_tracker.track_features(np.asarray(cv2.imread(img)))
        if len(feature_tracker.get_good_new()) == 0:
            break
        feature_tracker.cluster()
        feature_tracker.average()
        feature_tracker.update()

        markers = np.zeros_like(feature_tracker.get_frame_gray())
        for point in feature_tracker.get_pen_tip():
            cv2.circle(feature_tracker.get_frame(), tuple(point), 5, (0,0,255), 2)

        cv2.imshow('frame',cv2.resize(feature_tracker.get_frame(), (0,0), fx=0.5, fy=0.5))
        time.sleep(0.1)
        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break


if __name__ == "__main__":
    main()
