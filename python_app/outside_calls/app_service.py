# start the rpyc server
import rpyc
import time

def processLink(message, *args):
    print("Hello: " + message)

class MyService(rpyc.Service):
    def exposed_processLink(self, message, *args):
        return processLink(message, *args)

from rpyc.utils.server import ThreadedServer
from threading import Thread

server = ThreadedServer(MyService, port = 12345)
t = Thread(target = server.start)
t.daemon = True
t.start()

while True:
    time.sleep(1)