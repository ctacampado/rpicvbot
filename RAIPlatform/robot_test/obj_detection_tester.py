__author__ = 'ctacampado'

import cv2
import os.path
import threading
import socket
import socketserver
import numpy as np
import re

class ThreadServer(object):
    
    def __init__(self, host, port, action):
        self.server = socketserver.TCPServer((host, port), action)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server.serve_forever()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()

    def start(self):
        self.server_thread.start()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()

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
            scaleFactor=2,  
            minNeighbors=7,
            minSize=(100, 100),
            maxSize=(110, 110)
            #flags=cv2.CASCADE_SCALE_IMAGE
        )

        #cascade_obj = cascade_classifier.detectMultiScale(gray_image, 1.3, 5)

        # draw a rectangle around the objects
        for (x_pos, y_pos, width, height) in cascade_obj:
            cv2.rectangle(image, (x_pos+2, y_pos+2), (x_pos+width-2, y_pos+height-2), (255, 255, 0), 2)
            v = y_pos + height - 2

            # image
            
            if width/height == 1:
                cv2.putText(image, 'CUBE', (x_pos, y_pos-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            break
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
                    cv2.imshow('image', image)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
        finally:
            self.connection.close()
            self.server_socket.close()

if __name__ == '__main__':
    print ('starting Object Detection Tester...')
    VideoStreamHandler()
    print ('Thread server closed!')