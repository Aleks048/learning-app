# start the rpyc server
import rpyc
import time

import outside_calls.url as url

def processLink(*args):
    url.processLinkCall(args[0], args[1], args[2], args[3])

class MyService(rpyc.Service):
    def exposed_processLink(self, *args):
        return processLink(*args)

from rpyc.utils.server import ThreadedServer
from threading import Thread

server = ThreadedServer(MyService, port = 12345)
t = Thread(target = server.start)
t.daemon = True
t.start()

while True:
    time.sleep(1)