__author__ = 'ctacampado'

import cv2
import os.path

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

        #cascade_obj = cascade_classifier.detectMultiScale(
        #    gray_image,
        #    scaleFactor=1.1,  
        #    minNeighbors=300,
        #    minSize=(70, 70),
        #    #maxSize=(130, 130),
        #    flags=cv2.CASCADE_SCALE_IMAGE
        #)
        cascade_obj = cascade_classifier.detectMultiScale(
            gray_image,
            scaleFactor=1.1,  
            minNeighbors=5,
            minSize=(30, 30),
            #maxSize=(130, 130),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        #print(cascade_obj)
        #mylist = list(cascade_obj)
        #print(mylist)
        #thresh = 0
        #result, weights = cv2.groupRectangles(mylist, thresh, 0)

        # draw a rectangle around the objects
        #print(result)
        #print(weights)
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
