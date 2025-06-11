import os, json, subprocess
from threading import Thread

import platform

if platform.system() == "Darwin":
    from AppKit import NSScreen
elif platform.system() == "Windows":
    import ctypes

from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

import pytesseract
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"  # your path may be different

from oslo_concurrency import lockutils

import _utils.logging as log

def getMonitorsAreas():
    def __getMonitorsAreas_win():
        # adapted from https://stackoverflow.com/a/65256327
        user = ctypes.windll.user32

        class RECT(ctypes.Structure):
            _fields_ = [
                ('left', ctypes.c_long),
                ('top', ctypes.c_long),
                ('right', ctypes.c_long),
                ('bottom', ctypes.c_long)
                ]
            def dump(self):
                return [int(val) for val in (self.left, self.top, self.right, self.bottom)]

        class MONITORINFO(ctypes.Structure):
            _fields_ = [
                ('cbSize', ctypes.c_ulong),
                ('rcMonitor', RECT),
                ('rcWork', RECT),
                ('dwFlags', ctypes.c_ulong)
                ]

        def get_monitors():
            retval = []
            CBFUNC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong, ctypes.POINTER(RECT), ctypes.c_double)
            def cb(hMonitor, hdcMonitor, lprcMonitor, dwData):
                r = lprcMonitor.contents
                #print("cb: %s %s %s %s %s %s %s %s" % (hMonitor, type(hMonitor), hdcMonitor, type(hdcMonitor), lprcMonitor, type(lprcMonitor), dwData, type(dwData)))
                data = [hMonitor]
                data.append(r.dump())
                retval.append(data)
                return 1
            cbfunc = CBFUNC(cb)
            temp = user.EnumDisplayMonitors(0, 0, cbfunc, 0)
            return retval

        retval = []
        monitors = get_monitors()
        for hMonitor, extents in monitors:
            data = [hMonitor]
            mi = MONITORINFO()
            mi.cbSize = ctypes.sizeof(MONITORINFO)
            mi.rcMonitor = RECT()
            mi.rcWork = RECT()
            res = user.GetMonitorInfoA(hMonitor, ctypes.byref(mi))
            data = mi.rcMonitor.dump()
        #    data.append(mi.rcWork.dump())
            retval.append(data)
        return retval

    def __getMonitorsAreas_mac():
        monitors = [[0, 0, int(screen.frame().size.width), int(screen.frame().size.height)] for screen in NSScreen.screens()]
        sum = 0
        for m in monitors:
            m[1] = sum
            sum += m[3]
        
        return monitors

    if platform.system() == "Darwin":
       return __getMonitorsAreas_mac()
    elif platform.system() == "Windows":
        return __getMonitorsAreas_win()

class Token:
    class NotDef:
        no_t = None
        int_t = -1
        str_t = "-1"
        list_t = [str_t]
        dict_t = {str_t: str_t}

def getTextFromImage(imPath, pilImg = None):
    if pilImg == None:
        pilImg = Image.open(imPath)

    text:str = pytesseract.image_to_string(pilImg)
    pilImg.close()

    textList = text.split("\n")
    text = ""
    for l in textList:
        if l != "":
            text += l
        else:
            text += "\n"

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
    if platform.system() == "Darwin":
        # NOTE: this is an alternative way to get screen size. Might be better?
        return [(screen.frame().size.width, screen.frame().size.height)
                for screen in NSScreen.screens()][0]
    elif platform.system() == "Windows":
        user32 = ctypes.windll.user32
        return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    else:
        return None

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


def filePathToParentDir(fp):
    '''
    returns path to the parrent directory from the fp
    '''
    return os.path.join(*fp.split("/")[:-1])


def getPathToBooks():
    return os.getenv("BOOKS_ROOT_PATH")


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
        if filePath not in list(cls.__tempFiles.keys()):
            outputList = None

            with open(filePath, 'r') as f:
                outputList = json.loads(f.read())
                cls.__tempFiles[filePath] = outputList

            return outputList
        else:
            return cls.__tempFiles[filePath].copy()

    @classmethod
    def writeFile(cls, filePath, dataTowrite):
        cls.__tempFiles[filePath] = dataTowrite

    @lockutils.synchronized('not_thread_safe')
    def readProperty(jsonFilepath, propertyName):
        jsonData = JSON.readFile(jsonFilepath).copy()
        
        def _readProperty(jsonData):
            if propertyName in jsonData:
                out = jsonData[propertyName]

                if type(out) != str and type(out) != int  and type(out) != bool:
                    return jsonData[propertyName].copy()
                else:
                    return jsonData[propertyName]

            for k, v in jsonData.items():
                if type(v) is list:
                    if v == [] or type(v[0]) is str:
                        if propertyName == k:
                            if type(v) != str and type(v) != int and type(v) != bool:
                                return v.copy()
                            else:
                                return v
                    else:
                        for i in v:
                            property = _readProperty(i)
                            if property != None:
                                if type(property) != str and type(property) != int  and type(property) != bool:
                                    return property.copy()
                                else:
                                    return property
                elif type(v) is dict:
                    property = _readProperty(v)
                    if property != None:
                        if type(property) != str and type(property) != int and type(property) != bool:
                            return property.copy()
                        else:
                            return property
        property = _readProperty(jsonData)

        if type(property) != str and type(property) != int and type(property) != bool:
            return property.copy()
        else:
            return property

    @lockutils.synchronized('not_thread_safe')
    def updateProperty(jsonFilepath, propertyName, newValue):
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
                    if type(jsonData[propertyName]) == str:
                        jsonData[propertyName] = str(newValue)
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
    def createProperty(jsonFilepath, propertyName, parentName, defaultValue):
        jsonData = JSON.readFile(jsonFilepath)

        if parentName != None:
            jsonData[parentName][propertyName] = defaultValue
        else:
            jsonData[propertyName] = defaultValue

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