__author__ = 'ctacampado'

import cv2
import os.path

class ObjectClassifier():
    
    def __init__(self, name, path):
        self.name = name
        print 'initializing %s Classifier...' % self.name,
        self.path = path
        print 'done!'

    def create(self):
        print 'Creating %s Classifier...' % self.name,
        #load classifier model
        if os.path.isfile(self.path):
            self.classifier = cv2.CascadeClassifier(self.path)
            print 'done!'
            return 0
        else:
            print 'failed to load %s Classifier model from %s' % (self.name, self.path)
            return 1


