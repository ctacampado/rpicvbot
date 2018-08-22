__author__ = 'ctacampado'

import cv2
import math
import json
import os.path

class ObjDistanceCalc(object):
  
    def __init__(self):
        print 'initializing Object Distance Calculator...',
        self.path = '../../robot_test/cam_callibration/cam_params.json' 
        print 'done!'

    def create(self):
        print 'creating Object Distance Calculator...',
        if os.path.isfile(self.path):
            with open('../../robot_test/cam_callibration/cam_params.json') as p:
                self.cparam = json.load(p)
            
            self.alpha = 8.0 * math.pi / 180
            self.v0 = self.cparam["v0"]
            self.ay = self.cparam["ay"]
            print 'done!'
            return 0
        else:
            print 'failed to load Object Distance Calculator config from %s' % self.path
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