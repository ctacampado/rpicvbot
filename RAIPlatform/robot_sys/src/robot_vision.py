__author__ = 'ctacampado'

import cv2
import numpy as np
import math
import json
import os.path

def extractImageFromStream(stream_bytes):
    first = stream_bytes.find(b'\xff\xd8')
    last = stream_bytes.find(b'\xff\xd9')
    if first != -1 and last != -1:
        jpg = stream_bytes[first:last+2]
        stream_bytes = stream_bytes[last+2:]
        gray = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
        image = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        return True, stream_bytes, gray, image
    return False, stream_bytes, None, None

class ObjDistanceCalc(object):
  
    def __init__(self):
        print ('initializing Object Distance Calculator...', end="", flush=True)
        self.path = '../../robot_test/cam_callibration/cam_params.json'
        print ('done!')

    def create(self):
        print ('creating Object Distance Calculator...', end="", flush=True)
        if os.path.isfile(self.path):
            with open(self.path) as p:
                self.cparam = json.load(p)
            
            self.alpha = 8.0 * math.pi / 180
            self.v0 = self.cparam["v0"]
            self.ay = self.cparam["ay"]
            print ('done!')
            return 0
        else:
            print ('failed to load Object Distance Calculator config from %s' % self.path)
            return 1

    def calculate(self, v, h, x_shift, image):
        # compute and return the distance from the target point to the camera
        d = h / math.tan(self.alpha + math.atan((v - self.v0) / self.ay))
        if d > 0:
            cv2.putText(image, "%.1fcm" % d,
                (image.shape[1] - x_shift, image.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        return d

    def getCameraSpecs(self):
    	print("#####Camera Specs#####")
    	print("alpha: %f" % self.alpha)
    	print("v0: %f" % self.v0)
    	print("ay: %f" % self.ay)
    	print("######################")


class ObjectClassifier():
    
    def __init__(self, name, path):
        self.name = name
        print ('initializing %s Classifier...' % self.name, end="", flush=True)
        self.path = path

        self.red_light = False
        self.green_light = False
        self.yellow_light = False
        print ('done!')

    def create(self):
        print ('Creating %s Classifier...' % self.name),
        #load classifier model
        if os.path.isfile(self.path):
            self.classifier = cv2.CascadeClassifier(self.path)
            print ('done!')
            return 0
        else:
            print ('failed to load %s Classifier model from %s' % (self.name, self.path))
            return 1

    def detect(self, cascade_classifier, gray_image, image):
        v = 0
        threshold = 150

        # detection  
        cascade_obj = cascade_classifier.detectMultiScale(
            gray_image,
            scaleFactor=1.1,  
            minNeighbors=5,
            minSize=(30, 30),
            #maxSize=(130, 130),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        for (x_pos, y_pos, width, height) in cascade_obj:
            cv2.rectangle(image, (x_pos+5, y_pos+5), (x_pos+width-5, y_pos+height-5), (255, 255, 0), 2)
            v = y_pos + height - 5

            # stop sign
            if width/height == 1:
                cv2.putText(image, self.name, (x_pos, y_pos-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # traffic light
            else:
                roi = gray_image[y_pos + 10:y_pos + height - 10, x_pos + 10:x_pos + width - 10]
                mask = cv2.GaussianBlur(roi, (25, 25), 0)
                (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(mask)
                # check if light is on
                if maxVal - minVal > threshold:
                    cv2.circle(roi, maxLoc, 5, (255, 0, 0), 2)

                    # Red light
                    if 1.0 / 8 * (height - 30) < maxLoc[1] < 4.0 / 8 * (height - 30):
                        cv2.putText(image, 'Red', (x_pos + 5, y_pos - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                        self.red_light = True

                    # Green light
                    elif 5.5 / 8 * (height - 30) < maxLoc[1] < height - 30:
                        cv2.putText(image, 'Green', (x_pos + 5, y_pos - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0),2)
                        self.green_light = True

                # unknown
                #else:
                    #cv2.putText(image, 'N/A', (x_pos + 5, y_pos +5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0),2)
        return v
