import sys, os, json, time, subprocess
from threading import Thread
from screeninfo import get_monitors
from AppKit import NSWorkspace
import Quartz

import _utils.logging as log

class Token:
    class NotDef:
        str_t = "-1"
        list_t = [str_t]
        dict_t = {str_t: str_t}

def runCmdAndWait(cmd):
    t = Thread(target = lambda *args: subprocess.Popen(cmd, shell = True))
    t.start()
    t.join()

def findPositionsOfMarkerInFile(filepath, marker, lineToken = ""):
    outPos = []

    if not os.path.exists(filepath):
        log.autolog("filepath does not exist. \nfilepath: " + filepath)
        return None, None
    with open(filepath, "r") as f:
        fLines = f.readlines()
     
    for i in range(len(fLines)):
        if  marker in fLines[i] and lineToken in fLines[i]:
            outPos.append(i)
    
    return outPos, fLines



def replaceMarkerInFile(filepath, marker, value, lineToken = ""):
    outPos, fLines = findPositionsOfMarkerInFile(filepath, marker, lineToken)

    if outPos == None or fLines == None:
        return
    
    for i in range(len(fLines)):
        if i in outPos:
            fLines[i] = fLines[i].replace(marker, value)
    
    with open(filepath, "w") as f:
        f.writelines(fLines)


def getMonitorSize():
    for m in get_monitors():
       return(m.width,m.height)


def readFile(fp):
    '''
    read the fp to lines list
    '''
    #!!!!!NOTE: the relationship with the env var needs to change

    with open(fp, "r") as file:
        # read the temptate file
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]
        return lines


def readPyArgs():
    '''
    read the arguments proveded to the python script to a readToList
    '''
    readToList = []
    for i in range(1, len(sys.argv)):
        readToList.append(sys.argv[i])
    return readToList


def filePathToParentDir(fp):
    '''
    returns path to the parrent directory from the fp
    '''
    return os.path.join(*fp.split("/")[:-1])


def getPathToBooks():
    return os.getenv("BOOKS_ROOT_PATH")


def getAllRunningApps():
    #get all the running applications
    workspace = NSWorkspace.sharedWorkspace()
    activeApps = workspace.runningApplications()
    return activeApps


def getWindowsList():
    # if app.isActive():
    options = Quartz.kCGWindowListOptionOnScreenOnly
    return Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)


def getOwnersName_windowID_ofApp(appName, windowIdentifier = ""):
    activeApps = getAllRunningApps()
    
    app = [i for i in activeApps if appName in str(i).lower()]
    while len(app) == 0:
        time.sleep(0.1)
        activeApps = getAllRunningApps()
        app = [i for i in activeApps if appName in str(i).lower()]

    app = app[0]

    if app == None :
        log.autolog("getOwnersName_windowID_ofApp - the app was not found")
        return None, None, None
    
    windowList = getWindowsList()
    
    for window in windowList:
        if window["kCGWindowOwnerName"] == app.localizedName():
            if windowIdentifier in window["kCGWindowName"]:
                ownerName = str(window["kCGWindowOwnerName"])
                windowName = str(window["kCGWindowName"])
                ownerPID = str(window["kCGWindowOwnerPID"])            

                return ownerName, windowName, ownerPID
    
    # log.autolog("getOwnersName_windowID_ofApp - window was not found")
    return None, None, None


'''
JSON
'''
class JSON:
    def createFromTemplate(path, template):
        with open(path, "w+") as f:
            jsonObj = json.dumps(template, indent = 4)
            f.write(jsonObj)

    def readFile(filePath):
        # print("JSON.readFile - reading json file: " + filePath)
        with open(filePath, 'r') as f:
            outputList = json.loads(f.read())
            return outputList

    def writeFile(filePath, dataTowrite):
        # print("JSON.writeFile - writing to json file: " + filePath)
        with open(filePath, 'w') as f:
            jsonObj = json.dumps(dataTowrite, indent=4)
            f.write(jsonObj)

    def readProperty(jsonFilepath, propertyName):
        jsonData = JSON.readFile(jsonFilepath)
        
        def _readProperty(jsonData):
            if propertyName in jsonData:
                return jsonData[propertyName]
            for _, v in jsonData.items():
                if type(v) is list:
                    for i in v:
                        property = _readProperty(i)
                        if property != None:
                            return property
                elif type(v) is dict:
                    property = _readProperty(v)
                    if property != None:
                        return property
        property = _readProperty(jsonData)
        return property

    def updateProperty(jsonFilepath, propertyName, newValue):
        # print("JSON.updateProperty - updating property " + propertyName + " in settings file")
    
        def _updateProperty(jsonData, newValue):
            if propertyName in jsonData:
                if type(newValue) != type(jsonData[propertyName]):
                    log.autolog("\
    ERROR: JSON.updateProperty - did not update the json file. \
    Type of new value type '{0}' does not match the type of the property '{1}'".format(type(newValue), type(jsonData[propertyName])))
                else:
                    jsonData[propertyName] = newValue
            else:
                for k, v in jsonData.items():
                    if type(v) is list:
                        for i in range(len(v)):
                            if v[i] is dict or v[i] is list:
                                _updateProperty(v[i], newValue)
                    elif type(v) is dict:
                        _updateProperty(v, newValue)
        
        jsonData = JSON.readFile(jsonFilepath)
        _updateProperty(jsonData, newValue)
        JSON.writeFile(jsonFilepath, jsonData)

'''
DICT
'''
class DICT:
    def readProperty(dictToReadFrom, propertyName):
        if propertyName in dictToReadFrom:
            return dictToReadFrom[propertyName]
        for _, v in dictToReadFrom.items():
            if type(v) is list:
                for i in v:
                    property = DICT.readProperty(i, propertyName)
                    if property != None:
                        return property
            elif type(v) is dict:
                property = DICT.readProperty(v, propertyName)
                if property != None:
                    return property

    def updateProperty(dictToUpdate, propertyName, newValue):
        if propertyName in dictToUpdate:
            if type(newValue) != type(dictToUpdate[propertyName]):
                    log.autolog("\
    ERROR: JSON.updateProperty - did not update the json file. \
    Type of new value does not match the type of the property")
            else:
                dictToUpdate[propertyName] = newValue
        else:
            for k, v in dictToUpdate.items():
                if type(v) is list:
                    for i in range(len(v)):
                        if v[i] is dict or v[i] is list:
                            DICT.updateProperty(v[i], propertyName, newValue)
                elif type(v) is dict:
                    DICT.updateProperty(v, propertyName, newValue)