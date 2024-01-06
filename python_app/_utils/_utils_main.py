import sys, os, json, time, subprocess
from threading import Thread
from AppKit import NSScreen, NSWorkspace
import Quartz
from PIL import Image
import pytesseract
from oslo_concurrency import lockutils

import _utils.logging as log

class Token:
    class NotDef:
        int_t = -1
        str_t = "-1"
        list_t = [str_t]
        dict_t = {str_t: str_t}

def getTextFromImage(imPath):
    pilImg = Image.open(imPath)
    text = pytesseract.image_to_string(pilImg)
    pilImg.close()
    return text

def runCmdAndWait(cmd):
    t = Thread(target = lambda *args: subprocess.Popen(cmd, shell = True))
    t.start()
    t.join()

def runCmdAndGetResult(cmd, stdout = subprocess.PIPE, stderr = None):
    p = subprocess.Popen(cmd, shell= True, stdout= stdout, stderr= stderr)
    result, error = p.communicate()
    
    if result != None:
        result = result.decode("utf-8")
    
    if error != None:
        error = error.decode("utf-8")
    
    return result, error

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
        log.autolog("Could not find line token '{0}' in '{1}'".format(lineToken, filepath))
        return
    
    for i in range(len(fLines)):
        if i in outPos:
            fLines[i] = fLines[i].replace(marker, value)
    
    with open(filepath, "w") as f:
        f.writelines(fLines)


def getMonitorSize():
    # NOTE: this is an alternative way to get screen size. Might be better?
    # from screeninfo import get_monitors
    # import tkinter
    # root = tkinter.Toplevel()
    # root.withdraw()
    # return [root.winfo_screenwidth(), root.winfo_screenheight()]
    return [(screen.frame().size.width, screen.frame().size.height)
            for screen in NSScreen.screens()][0]

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


def getOwnersName_windowID_ofApp(appName:str, windowIdentifier = ""):
    activeApps = getAllRunningApps()
    
    app = [i for i in activeApps if appName.lower() in str(i).lower()]
    counter = 0
    while len(app) == 0 and counter < 5:
        time.sleep(0.1)
        activeApps = getAllRunningApps()
        app = [i for i in activeApps if appName.lower() in str(i).lower()]
        counter += 1
    
    if len(app) < 1:
        log.autolog("could not get the PID for '{0}'. Please open the app. 1".format(appName))
        return None, None, None

    app = app[0]

    if app == None :
        log.autolog("could not get the PID for '{0}'. Please open the app. 2".format(appName))
        return None, None, None
    
    windowList = getWindowsList()
    
    for window in windowList:
        if window["kCGWindowOwnerName"].lower() == app.localizedName().lower():
            if windowIdentifier.lower() in window["kCGWindowName"].lower():
                ownerName = str(window["kCGWindowOwnerName"])
                windowName = str(window["kCGWindowName"])
                ownerPID = str(window["kCGWindowOwnerPID"])            

                return ownerName, windowName, ownerPID
    
    # log.autolog("getOwnersName_windowID_ofApp - window was not found")
    log.autolog("could not get the PID for '{0}'. Please open the app. 3".format(appName))
    return None, None, None


'''
JSON
'''
class JSON:
    __tempFiles = {}

    @classmethod
    def reloadFilesFromDisk(cls):
        import outside_calls.outside_calls_facade as ocf
        paths = list(cls.__tempFiles.keys()).copy()
        cls.__tempFiles = {}

        for fp in paths:
            if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(fp):
                cls.readFile(fp)

    @classmethod
    def saveFilesToDisk(cls):
        import outside_calls.outside_calls_facade as ocf

        for fp, data in cls.__tempFiles.items():
            if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(fp):
                with open(fp, 'w') as f:
                    jsonObj = json.dumps(data, indent=4)
                    f.write(jsonObj)

    def createFromTemplate(path, template):
        with open(path, "w+") as f:
            jsonObj = json.dumps(template, indent = 4)
            f.write(jsonObj)

    @classmethod
    def readFile(cls, filePath):
        # print("JSON.readFile - reading json file: " + filePath)

        if filePath not in list(cls.__tempFiles.keys()):
            with open(filePath, 'r') as f:
                outputList = json.loads(f.read())
                cls.__tempFiles[filePath] = outputList
                return outputList
        else:
            return cls.__tempFiles[filePath].copy()

    @classmethod
    def writeFile(cls, filePath, dataTowrite):
        # print("JSON.writeFile - writing to json file: " + filePath)
        cls.__tempFiles[filePath] = dataTowrite

    @lockutils.synchronized('not_thread_safe')
    def readProperty(jsonFilepath, propertyName):
        jsonData = JSON.readFile(jsonFilepath)
        
        def _readProperty(jsonData):
            if propertyName in jsonData:
                out = jsonData[propertyName]

                if type(out) != str and type(out) != int:
                    return jsonData[propertyName].copy()
                else:
                    return jsonData[propertyName]

            for k, v in jsonData.items():
                if type(v) is list:
                    if v == [] or type(v[0]) is str:
                        if propertyName == k:
                            if type(v) != str and type(v) != int:
                                return v.copy()
                            else:
                                return v
                    else:
                        for i in v:
                            property = _readProperty(i)
                            if property != None:
                                if type(property) != str and type(property) != int:
                                    return property.copy()
                                else:
                                    return property
                elif type(v) is dict:
                    property = _readProperty(v)
                    if property != None:
                        if type(property) != str and type(property) != int:
                            return property.copy()
                        else:
                            return property
        property = _readProperty(jsonData)

        if type(property) != str and type(property) != int:
            return property.copy()
        else:
            return property

    @lockutils.synchronized('not_thread_safe')
    def updateProperty(jsonFilepath, propertyName, newValue):
        # print("JSON.updateProperty - updating property " + propertyName + " in settings file")
    
        def _updateProperty(jsonData, newValue):
            if propertyName in jsonData:
                if type(newValue) != type(jsonData[propertyName]):
                    log.autolog("\
    ERROR: JSON.updateProperty - did not update the json file.\n\
    Type of new value '{4}' has type '{0}'\n\
    does not match the type of the property '{1}'\n\
    with name '{2}' The jsonPath '{3}'"\
                                .format(type(newValue),
                                        type(jsonData[propertyName]),
                                        propertyName,
                                        jsonFilepath,
                                        newValue))
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

    @lockutils.synchronized('not_thread_safe')
    def createProperty(jsonFilepath, propertyName, parentName):
        # TODO: a feature to create json property when its not there
        # NOTE: this might lead to inconsistency in data but we will be able to add 
        #       new properties to existing sections without much problems
        pass
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

    def updateProperty(dictToUpdate:dict, propertyName, newValue):
        if propertyName in dictToUpdate:
            if newValue == None:
                dictToUpdate.pop(propertyName)
            else:
                if type(newValue) != type(dictToUpdate[propertyName]):
                        log.autolog("\
        ERROR: JSON.updateProperty - did not update the json file. \
        Type of new value does not match the type of the property")
                else:
                    dictToUpdate[propertyName] = newValue
            return
        else:
            for k, v in dictToUpdate.items():
                if type(v) is list:
                    for i in range(len(v)):
                        if v[i] is dict or v[i] is list:
                            DICT.updateProperty(v[i], propertyName, newValue)
                elif type(v) is dict:
                    DICT.updateProperty(v, propertyName, newValue)