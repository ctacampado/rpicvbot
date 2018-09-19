__author__ = 'ctacampado'

import cv2
import math
import json
import os.path
import threading
import socket
import socketserver
import numpy as np
import re


class ObjDistanceCalc(object):
  
    def __init__(self):
        print ('initializing Object Distance Calculator...', end="", flush=True)
        self.path = 'cam_callibration/cam_params.json'
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
        # detection

        cascade_obj = cascade_classifier.detectMultiScale(
            gray_image,
            scaleFactor=1.1,  
            minNeighbors=300,
            minSize=(70, 70),
            #maxSize=(130, 130),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        #print(cascade_obj)
        mylist = list(cascade_obj)
        #print(mylist)
        thresh = 0
        result, weights = cv2.groupRectangles(mylist, thresh, 0)

        # draw a rectangle around the objects
        #print(result)
        #print(weights)
        for (x_pos, y_pos, width, height) in result:
            cv2.rectangle(image, (x_pos+2, y_pos+2), (x_pos+width-2, y_pos+height-2), (255, 255, 0), 2)
            v = y_pos + height - 2

            # image
            if width/height == 1:
                cv2.putText(image, 'CUBE', (x_pos, y_pos-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            #break
        return v

class VideoStreamHandler(object):

    def __init__(self):
        self.server_socket = socket.socket()
        self.server_socket.bind(('192.168.43.95', 3001))
        self.server_socket.listen(0)
        self.connection, self.client_address = self.server_socket.accept()
        self.connection = self.connection.makefile('rb')
        self.handle()
        
    def handle(self):
        print("handler function")
        h1 = 15.5 - 8
        distanceCalc = ObjDistanceCalc()
        ret = distanceCalc.create()

        cascade_path = '../robot_ai/obj_classifier/model/cascade.xml'
        cubeCascade = ObjectClassifier('Cube',  cascade_path)
        ret = cubeCascade.create()
        #byte_arr = bytearray()
        stream_bytes = bytes()
        # stream video frames one by one
        try:
            while True:
                stream_bytes += self.connection.read(1024)
                #stream_bytes = bytes(byte_arr)
                first = stream_bytes.find(b'\xff\xd8')
                last = stream_bytes.find(b'\xff\xd9')
                if first != -1 and last != -1:
                    jpg = stream_bytes[first:last+2]
                    stream_bytes = stream_bytes[last+2:]
                    gray = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
                    image = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_UNCHANGED)

                    # object detection
                    v_param1 = cubeCascade.detect(cubeCascade.classifier, gray, image)
                    # distance measurement
                    if v_param1 > 0:
                        d1 = distanceCalc.calculate(v_param1, h1, 300, image)
                       # print(d1)

                    cv2.imshow('image', image)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
        finally:
            self.connection.close()
            self.server_socket.close()

if __name__ == '__main__':
    print ('starting Object Distance Calculator Tester...')
    VideoStreamHandler()
    print ('Thread server closed!')