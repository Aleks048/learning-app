# start the rpyc server
import rpyc
from rpyc.utils.server import ThreadedServer
from threading import Thread
'''
here we make the wrappers for main app functions
so that they can be called by other apps
'''

import daemon_service.services_collection.url_request as url
import daemon_service.services_collection.vsCode_request as vscode
import daemon_service.services_collection.populateMainTeFile_request as ptf

class MyService(rpyc.Service):
    def exposed_processLink(self, urlLink):
        return url.processCall(urlLink)
    
    def exposed_processSaveTexFile(self, callerTexFile):
        return ptf.processCall(callerTexFile)

    def exposed_processVsCodeCall(self, vsCodeFilePath, shouldDelete):
        return vscode.processCall(vsCodeFilePath, shouldDelete)

def startMainServerDaemon(port = 12345):
    server = ThreadedServer(MyService, port = port)
    t = Thread(target = server.start)
    t.daemon = True
    t.start()
    return t, server