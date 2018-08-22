__author__ = 'ctacampado'

import numpy as np
import cv2
import socket
import pygame
from pygame.locals import KEYDOWN
#from pygame.locals import *
import socket
import time
import os
import io
import json
from PIL import Image

def bytes_to_surface(jpg):
    image = np.array(Image.open(io.BytesIO(jpg)))
    cv2.flip(image,1,image)
    image=np.rot90(image) 
    surf = pygame.surfarray.make_surface(image)
    return surf

class CollectData(object):
    def __init__(self):
        pygame.init()

        with open('config.json') as c:
            config = json.load(c)

        self.server_socket = socket.socket()
        self.server_socket.bind((config["serveraddr"], config["port"]))
        self.server_socket.listen(0)
        self.connection, self.client_address = self.server_socket.accept()
        self.connection = self.connection.makefile('rb')

        self.send_inst = True

        # create labels
        self.k = np.zeros((4, 4), 'float')
        for i in range(4):
            self.k[i, i] = 1
        self.temp_label = np.zeros((1, 4), 'float')

        self.collect_image()

    def collect_image(self):
        saved_frame = 0
        total_frame = 0

        screen = pygame.display.set_mode((320, 240))

        # collect images for training
        print 'Start collecting images...'
        e1 = cv2.getTickCount()
        image_array = np.zeros((1, 38400))
        label_array = np.zeros((1, 4), 'float')

        try:
            print "Connection from: ", self.client_address
            print "Streaming..."
            print "Press 'q' to exit"
            stream_bytes = ' '
            frame = 1
            while self.send_inst:
                stream_bytes += self.connection.read(1024)
                first = stream_bytes.find('\xff\xd8')
                last = stream_bytes.find('\xff\xd9')
                if first != -1 and last != -1:
                    jpg = stream_bytes[first:last + 2]
                    stream_bytes = stream_bytes[last + 2:]
                    #image = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.CV_LOAD_IMAGE_GRAYSCALE)
                    image = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
                    #cv2.imshow('image', image)
                    # save streamed images
                    roi = image[120:240, :]
                    cv2.imwrite('training_images/frame{:>05}.jpg'.format(frame), image)

                    screen.blit(bytes_to_surface(jpg),(0,0))
                    pygame.display.flip()

                    # reshape the roi image into one row array
                    temp_array = roi.reshape(1, 38400).astype(np.float32)
                    
                    frame += 1
                    total_frame += 1

                    for event in pygame.event.get():
                        if event.type == KEYDOWN:
                            print 'KEYDOWN'
                         # simple orders
                            if event.key == pygame.K_UP:
                                print('Up was pressed')
                                saved_frame += 1
                                image_array = np.vstack((image_array, temp_array))
                                label_array = np.vstack((label_array, self.k[2]))
                                
                            elif event.key == pygame.K_DOWN:
                                saved_frame += 1
                                image_array = np.vstack((image_array, temp_array))
                                label_array = np.vstack((label_array, self.k[3]))
                                print('Down was pressed')
                            
                            elif event.key == pygame.K_RIGHT:
                                print('Right was pressed')
                                image_array = np.vstack((image_array, temp_array))
                                label_array = np.vstack((label_array, self.k[1]))
                                saved_frame += 1

                            elif event.key == pygame.K_LEFT:
                                print('Left was pressed')
                                image_array = np.vstack((image_array, temp_array))
                                label_array = np.vstack((label_array, self.k[0]))
                                saved_frame += 1

                            elif event.key == pygame.K_x or event.key == pygame.K_q:
                                print('q || x was pressed')
                                self.send_inst = False
                                break
                                    
                        #elif event.type == pygame.KEYUP:
                            #print 'KEYUP'

            # save training images and labels
            train = image_array[1:, :]
            train_labels = label_array[1:, :]

            # save training data as a numpy file
            file_name = str(int(time.time()))
            directory = "training_data"
            if not os.path.exists(directory):
                os.makedirs(directory)
            try:    
                np.savez(directory + '/' + file_name + '.npz', train=train, train_labels=train_labels)
            except IOError as e:
                print(e)

            e2 = cv2.getTickCount()
            # calculate streaming duration
            time0 = (e2 - e1) / cv2.getTickFrequency()
            print 'Streaming duration:', time0

            print(train.shape)
            print(train_labels.shape)
            print 'Total frame:', total_frame
            print 'Saved frame:', saved_frame
            print 'Dropped frame', total_frame - saved_frame

        finally:
            self.connection.close()
            self.server_socket.close()

if __name__ == '__main__':
    CollectData()
