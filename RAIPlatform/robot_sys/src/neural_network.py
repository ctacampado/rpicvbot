__author__ = 'ctacampado'

import cv2
import numpy as np
import os.path

class NeuralNetwork(object):
  
    def __init__(self):
        print ('initializing NeuralNetwork...'),
        self.model = cv2.ml.ANN_MLP_create()
        self.path = '../robot_ai/ann/model/ann.xml'
        print ('done!')

    def create(self):
        print ('creating NeuralNetwork...'),
        dim = 38400
        layer_sizes = np.int32([dim, 32, 32, 4])
        self.model.setLayerSizes(layer_sizes)
        if os.path.isfile(self.path):
          self.model.load(self.path)
          print ('done!')
          return 0
        else:
          print ('failed to load Neural Network model from %s' % self.path)
          return 1

    def predict(self, samples):
        ret, resp = self.model.predict(samples)
        return resp.argmax(-1)