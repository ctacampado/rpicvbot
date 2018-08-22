__author__ = 'ctacampado'

import threading
import SocketServer
from robot import Robot

class ThreadServer():

    def server_thread(host, port, action):
        server = SocketServer.TCPServer((host, port), action)
        server.serve_forever()

    bot = Robot()
    bot.create()
    navigation_thread = threading.Thread(target=server_thread, args=('192.168.43.95', 3000, bot.navigate()))
    navigation_thread.start()

if __name__ == '__main__':
    ThreadServer()