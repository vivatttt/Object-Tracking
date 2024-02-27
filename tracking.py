#opencv-contrib-python
import cv2 
import os
from pathlib import Path
import numpy as np



def r_resize(shot, percent):
    height = shot.shape[0] * percent // 100
    width = shot.shape[1] * percent // 100

    return cv2.resize(shot, (width, height))

def main():
    video_name = 'traffic4.mp4'
    percent = 50

    dirname = os.path.dirname(__file__)
    video = os.path.join(dirname, str(Path('videos', video_name)))
  
    cap = cv2.VideoCapture(video)

    
    ret, frame = cap.read()

    trackers = []

    while True:
        
        ret, frame = cap.read()

        if not ret:
            break
        frame = r_resize(frame, percent)
    

        i = 0
        while i != len(trackers):
            _, box = trackers[i].update(frame)
            if sum(box) == 0:
                del trackers[i]
            else:
                (x, y, w, h) = [int(v) for v in box]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 255), 2, 1)
                i += 1

        cv2.imshow('tracking', frame)

        
        if cv2.waitKey(15) & 0xFF == ord('s'):
       
            roi = cv2.selectROI('tracking', frame)
            tracker = cv2.legacy.TrackerKCF_create()
            tracker.init(frame, roi)
            trackers.append(tracker)

        if (cv2.waitKey(15) & 0xFF == ord('q')):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()