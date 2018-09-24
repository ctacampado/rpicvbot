__author__ = 'ctacampado'

import sys
import time
import threading
import socketserver
from queue import Queue
from robot import Robot

if __name__ == '__main__':
    ip, p1, p2 = "192.168.43.95", 3001, 3002

    bot = Robot(ip, p1, p2)
    bot.create()
    bot.start()