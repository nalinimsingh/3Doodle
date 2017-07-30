import sys
import os
import time
import numpy as np
import cv2

def mask_image(orig_image):
  mask = np.all([orig_image[:,:,0]<100,orig_image[:,:,1]>100,orig_image[:,:,2]<100],axis=0)
  masked_image = orig_image*mask[:,:,np.newaxis]
  return masked_image

def main():
  dir = os.path.dirname(__file__)
  path = os.path.join(dir,'../mock/green_pen_manual/trial1')
  images = [os.path.join(path,f) for f in os.listdir(path) if not f.startswith('.')]
  xmin = 100
  xmax = 1650
  ymin = 150
  ymax = 1000

  feature_params = dict( maxCorners = 100,
                         qualityLevel = 0.00001,
                         minDistance = 5,
                         blockSize = 7 )

  lk_params = dict( winSize  = (5,5),
                    maxLevel = 10,
                    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 100, 0.05))

  # Find initial features
  old_frame = np.asarray(cv2.imread(images[0]))[ymin:ymax,xmin:xmax,:]
  old_masked = mask_image(old_frame)
  old_gray = cv2.cvtColor(old_masked, cv2.COLOR_BGR2GRAY)

  regenerate_features = False
  # Find initial features
  p0 = cv2.goodFeaturesToTrack(old_gray, mask = None, **feature_params)

  point_history = []

  for img in images[1:]:
      frame = np.asarray(cv2.imread(img))[ymin:ymax,xmin:xmax,:]
      frame_masked = mask_image(frame)
      frame_gray = cv2.cvtColor(frame_masked, cv2.COLOR_BGR2GRAY)

      # Calculate optical flow
      p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)

      # Select good points
      good_new = p1[st==1]

      if len(good_new)==0:
        break

      # Plot features
      markers = np.zeros_like(frame_gray)
      for point in good_new:
        cv2.circle(frame, tuple(point), 5, (0,0,255), 2)

      # Plot average
      avg = np.average(good_new,axis=0)
      point_history.append(avg)
      cv2.circle(frame_masked, tuple(avg), 5, (255,255,0), 2)

      # Show current frame    
      cv2.imshow('frame',cv2.resize(frame, (0,0), fx=0.5, fy=0.5))
      time.sleep(0.1)
      k = cv2.waitKey(30) & 0xff
      if k == 27:
          break

      old_gray = frame_gray.copy()

      p0 = good_new.reshape(-1,1,2)


  cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
