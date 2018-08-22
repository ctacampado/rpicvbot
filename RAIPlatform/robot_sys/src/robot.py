__author__ = 'ctacampado'

from neural_network import NeuralNetwork
from object_distance_calc import ObjDistanceCalc
from object_classifier import ObjectClassifier

class Robot():

  """
  initialize robot
  """
  def __init__(self):
    print 'Initializing Robot components...'
    self.createErrorCnt = 0
    self.nav_engine =  NeuralNetwork()
    self.dist_calc = ObjDistanceCalc()
    self.stopSign_classifier =  ObjectClassifier('StopSign','../robot_ai/obj_classifier/model/stop_sign.xml')
    self.trafficLight_classifier =  ObjectClassifier('TrafficLight','../robot_ai/obj_classifier/model/traffic_light.xml')
    print 'done initializing Robot components!'

  def create(self):
    print 'Creating Robot components...'
    self.createErrorCnt += self.nav_engine.create()
    self.createErrorCnt += self.dist_calc.create()
    self.createErrorCnt += self.stopSign_classifier.create()
    self.createErrorCnt += self.trafficLight_classifier.create()
    print '# of failed components: %d' % self.createErrorCnt
    print 'done creating Robot components!'
    print 'Robot now operational!'

  """
  navigation logic. this is the main system loop
  """
  def navigate(self):
    print 'Robot navigation started...'