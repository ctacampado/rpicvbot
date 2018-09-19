__author__ = 'ctacampado'

import time
import cv2
import socket
import numpy as np
from neural_network import NeuralNetwork
from object_distance_calc import ObjDistanceCalc
from object_classifier import ObjectClassifier

class Robot():

    """
    initialize robot
    """
    def __init__(self):
        print ('Initializing Robot components...',end="", flush=True)
        self.stopSignClassifier_path = '../../robot_ai/obj_classifier/model/stop_sign.xml'
        self.trafficLightClassifier_path = '../../robot_ai/obj_classifier/model/traffic_light.xml'
        self.cubeClassifier_path = '../../robot_ai/obj_classifier/model/cascade.xml'
        self.createErrorCnt = 0
        self.navFlag = True
        print ('done!')

    def create(self):
        print ('Creating Robot components...')
        self.nav_engine =  NeuralNetwork()
        self.dist_calc = ObjDistanceCalc()
        self.stopSign_classifier =  ObjectClassifier('StopSign', self.stopSignClassifier_path)
        self.trafficLight_classifier =  ObjectClassifier('TrafficLight', self.trafficLightClassifier_path)
        self.cube_classifier = ObjectClassifier('Cube', self.cubeClassifier_path)
        self.createErrorCnt += self.nav_engine.create()
        self.createErrorCnt += self.dist_calc.create()
        self.createErrorCnt += self.stopSign_classifier.create()
        self.createErrorCnt += self.trafficLight_classifier.create()
        self.createErrorCnt += self.cube_classifier.create()
        print ('# of failed components: %d' % self.createErrorCnt)
        print ('done creating Robot components!')
        print ('Robot now operational!')

    def start(self):
        self.server_socket = socket.socket()
        self.server_socket.bind(('192.168.43.95', 3001))
        self.server_socket.listen(0)
        print("waiting for rpi connection..."),
        self.connection, self.client_address = self.server_socket.accept()
        self.connection = self.connection.makefile('rb')
        self.navigate()

    """
    navigation logic. this is the main loop
    """
    def navigate(self):
        print ('connected!')
        h1 = 3.5
        stream_bytes = bytes()
        while self.navFlag:
            try:
                stream_bytes += self.connection.read(1024)
                first = stream_bytes.find(b'\xff\xd8')
                last = stream_bytes.find(b'\xff\xd9')
                if first != -1 and last != -1:
                    jpg = stream_bytes[first:last+2]
                    stream_bytes = stream_bytes[last+2:]
                    gray = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
                    image = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_UNCHANGED)

                    # object detection
                    #v_param1 = self.cube_classifier.detect(self.cube_classifier.classifier, gray, image)
                    v_param1 = self.stopSign_classifier.detect(self.stopSign_classifier.classifier, gray, image)
                    v_param2 = self.trafficLight_classifier.detect(self.trafficLight_classifier.classifier, gray, image)
                    # distance measurement
                    if v_param1 > 0 or v_param2 > 0:
                        #d1 = self.dist_calc.calculate(v_param1, h1, 300, image)
                        d1 = self.dist_calc.calculate(v_param1, h1, 300, image)
                        d2 = self.dist_calc.calculate(v_param2, h1, 100, image)
                       # print(d1)

                    cv2.imshow('image', image)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                # If `False`, the program is not blocked. `Queue.Empty` is thrown if 
                # the queue is empty
            except (KeyboardInterrupt, SystemExit):
                self.navFlag = False
                raise
        print ('stopping navigation...')
