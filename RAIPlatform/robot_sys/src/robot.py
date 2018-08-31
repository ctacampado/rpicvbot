__author__ = 'ctacampado'

import time
import queue
from neural_network import NeuralNetwork
from object_distance_calc import ObjDistanceCalc
from object_classifier import ObjectClassifier

class Robot():

    """
    initialize robot
    """
    def __init__(self):
        print ('Initializing Robot components...')
        stopSignClassifier_path = '../robot_ai/obj_classifier/model/stop_sign.xml'
        trafficLightClassifier_path = '../robot_ai/obj_classifier/model/traffic_light.xml'
        self.createErrorCnt = 0
        self.navFlag = True
        self.nav_engine =  NeuralNetwork()
        self.dist_calc = ObjDistanceCalc()
        self.stopSign_classifier =  ObjectClassifier('StopSign', stopSignClassifier_path)
        self.trafficLight_classifier =  ObjectClassifier('TrafficLight', trafficLightClassifier_path)
        print ('done initializing Robot components!')

    def create(self):
        print ('Creating Robot components...')
        self.createErrorCnt += self.nav_engine.create()
        self.createErrorCnt += self.dist_calc.create()
        self.createErrorCnt += self.stopSign_classifier.create()
        self.createErrorCnt += self.trafficLight_classifier.create()
        print ('# of failed components: %d' % self.createErrorCnt)
        print ('done creating Robot components!')
        print ('Robot now operational!')

    """
    navigation logic. this is the main loop
    """
    def navigate(self, q):
        print ('Robot navigation started...')
        while self.navFlag:
            try:
                msg = q.get(False)
                # If `False`, the program is not blocked. `Queue.Empty` is thrown if 
                # the queue is empty
            except queue.Empty:
                print ('waiting...')
                time.sleep(1)
            else:
                self.navFlag = msg

        print ('stopping navigation...')
