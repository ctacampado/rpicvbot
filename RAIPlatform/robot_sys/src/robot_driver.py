__author__ = 'ctacampado'

import sys
import time
import threading
import SocketServer
from Queue import Queue
from robot import Robot

def stopper_thread(pill, q):
    time.sleep(3)
    try:
        raise Exception(False)
    except Exception:
        q.put(sys.exc_info())

class ThreadServer(object):
    
    def __init__(self, host, port, action):
        self.server = SocketServer.TCPServer((host, port), action)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True

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

if __name__ == '__main__':
    
    bot = Robot()
    bot.create()

    command_q = Queue()

    print 'starting dummy thread...',
    dummy_thread = threading.Thread(target=stopper_thread, args=(False, command_q))
    dummy_thread.start()
    print 'done!'

    print 'starting ThreadServer...'
    with ThreadServer("localhost", 3000, bot.navigate(command_q)) as server:
        print 'bot navigation stopped!'
    print 'Thread server closed!'