__author__ = 'ctacampado'

import sys
import time
import threading
import socketserver
from queue import Queue
from robot import Robot

if __name__ == '__main__':
    
    bot = Robot()
    bot.create()
    bot.start()

    #print ('starting Navigation thread... waiting for rpi...')
    #with ThreadServer('192.168.43.95', 3001, bot.navigate) as server:
    #    print ('bot navigation stopped!')
    #print ('Thread server closed!')
