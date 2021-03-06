__author__ = 'ctacampado'

import time
import cv2
import socket
import numpy as np
import sys
from neural_network import NeuralNetwork
from vision import extractImageFromStream, detectObjAndCalcDist, ObjDistanceCalc, ObjectClassifier
from concurrent.futures import ThreadPoolExecutor

def func():
    return sys._getframe().f_back.f_code.co_name

class Robot(object):

    """
    initialize robot
    """
    def __init__(self, ip, p1, p2):
        print ('Initializing Robot components...',end="", flush=True)
        self.stopSignClassifier_path = '../../robot_ai/obj_classifier/model/stop_sign.xml'
        self.trafficLightClassifier_path = '../../robot_ai/obj_classifier/model/traffic_light.xml'
        self.createErrorCnt = 0
        self.navFlag = True
        self.ip = ip
        self.p1 = p1
        self.p2 = p2
        self.servsock_v = socket.socket()
        self.servsock_s = socket.socket()
        self.sensor_data = 0
        print ('done!')

    def create(self):
        print ('Creating Robot components...')
        self.nav_engine =  NeuralNetwork()
        self.dist_calc = ObjDistanceCalc()
        self.stopSign_classifier =  ObjectClassifier('StopSign', self.stopSignClassifier_path)
        self.trafficLight_classifier =  ObjectClassifier('TrafficLight', self.trafficLightClassifier_path)
        self.createErrorCnt += self.nav_engine.create()
        self.createErrorCnt += self.dist_calc.create()
        self.createErrorCnt += self.stopSign_classifier.create()
        self.createErrorCnt += self.trafficLight_classifier.create()
        print ('# of failed components: %d' % self.createErrorCnt)
        print ('done creating Robot components!')
        print ('Robot now operational!')
    
    def start(self):
        self.servsock_s.bind((self.ip, self.p2))
        self.servsock_v.bind((self.ip, self.p1))
        self.servsock_v.listen(1)
        self.servsock_s.listen(1)
        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.submit(self.readFromSensor)
            executor.submit(self.startNavigation)
        print("all threads closed!")

    def waitForComponentConnection(self, component, socket):
        print("waiting for %s connection..." % component)
        connection, client_address = socket.accept()
        if (component != "us"):
            connection = connection.makefile('rb')
        print ('%s connected!' % component, client_address)
        return connection

    #move to sensors.py
    def readFromSensor(self):
        data = " "
        connection = self.waitForComponentConnection("us", self.servsock_s)
        while self.navFlag:
            try:
                data = connection.recv(1024)
                if not data: break
                self.sensor_data = round(float(data.decode()), 1)
                time.sleep(0.5)
            except (KeyboardInterrupt, SystemExit):
                self.navFlag = False
                break
        print ('closing %s thread...' % func())

    def startNavigation(self):
        connection = self.waitForComponentConnection("camera", self.servsock_v)
        h1 = 4
        h2 = 5.5
        stream_bytes = bytes()
        while self.navFlag:
            try:
                stream_bytes += connection.read(1024)
                if not stream_bytes: break
                img_is_ready, stream_bytes, gray, image = extractImageFromStream(stream_bytes)
                if img_is_ready:
                    v_param1, d1, image = detectObjAndCalcDist(h1, 300, gray, image, self.stopSign_classifier, self.dist_calc)
                    v_param2, d2, image = detectObjAndCalcDist(h2, 100, gray, image, self.trafficLight_classifier, self.dist_calc)
                    cv2.imshow('image', image)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        self.navFlag = False
                        break
            except (KeyboardInterrupt, SystemExit):
                self.navFlag = False
                raise
        self.servsock_s.close()
        print ('closing %s thread...' % func())