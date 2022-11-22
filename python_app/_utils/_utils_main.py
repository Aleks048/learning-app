import sys, os, json
from screeninfo import get_monitors
from AppKit import NSWorkspace
import Quartz

import file_system.file_system_manager as fsm
import _utils.logging as log

def getCurrSectionMoveNumber():
    currSection = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.currSection_ID)
    
    #check if section infostructure has file move numbers defined
    contentFileMoveNumber = fsm.Wr.SectionInfoStructure.readProperty(currSection, fsm.PropIDs.Sec.imageContentFileMoveLinesNumber_ID)
    tocFileMoveNumber = fsm.Wr.SectionInfoStructure.readProperty(currSection, fsm.PropIDs.Sec.imageTOCFileMoveLinesNumber_ID)

    if contentFileMoveNumber != notDefinedToken and tocFileMoveNumber != notDefinedToken:
        log.autolog("Got move numbers from section. Content: " + str(contentFileMoveNumber) + ". TOC: " + str(tocFileMoveNumber))
        
        #print to get values in sh script
        print(str(contentFileMoveNumber) + " "+ str(tocFileMoveNumber))
        return contentFileMoveNumber, tocFileMoveNumber
    
    #get the move numbers from bookinfostructure
    contentFileMoveNumber = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.imageContentFileMoveLinesNumber_ID)
    tocFileMoveNumber = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.imageTOCFileMoveLinesNumber_ID)
    
    log.autolog("Got move numbers from book. Content: " + str(contentFileMoveNumber) + ". TOC: " + str(tocFileMoveNumber))
    
    #print to get values in sh script
    print(str(contentFileMoveNumber) + " " + str(tocFileMoveNumber))
    return contentFileMoveNumber, tocFileMoveNumber

def replaceMarkerInFile(filepath, marker, value, lineToken = ""):
    if not os.path.exists(filepath):
        print("replaceMarkerInFile - filepath does not exist.")
        print("filepath: " + filepath)
        return None
    with open(filepath, "r") as f:
        fLines = f.readlines()
    
    for i in range(len(fLines)):
        if  marker in fLines[i] and lineToken in fLines[i]:
            fLines[i] = fLines[i].replace(marker, value)
    
    with open(filepath, "w") as f:
        f.writelines(fLines)

def getMonitorSize():
    for m in get_monitors():
       return(m.width,m.height)

notDefinedToken = "-1"

'''
DIR
'''
class DIR:
    class Section:
        @classmethod
        def getCurrentAbs(cls):
            relFilepath = cls.getCurrentRel()
            bookPath = Settings.readProperty(Settings.PubProp.currBookPath_ID)
            return os.path.join(bookPath, relFilepath)

        def getCurrentRel():
            currSec = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.currSection_ID)
            
            if currSec == notDefinedToken:              
                return ""
            
            filepath = fsm.Wr.BookInfoStructure.readProperty(currSec)["path"]
            bookpath = Settings.readProperty(Settings.PubProp.currBookPath_ID)

            relFilepath = filepath.replace(bookpath, "")
            relFilepath = os.path.join(*relFilepath.split("/")[:-1])
            return relFilepath

    class Screenshot:
        @classmethod
        def getCurrentRel(cls):
            currSection = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.currSection_ID)
            if currSection == notDefinedToken:
                return "Screenshot location not defined yet."
            else:
                return  os.path.join(DIR.Section.getCurrentRel(),getCurrentSectionNameWprefix() + "_images")

        @classmethod
        def getCurrentAbs(cls):
            return  os.path.join(DIR.Section.getCurrentAbs(), getCurrentSectionNameWprefix() + "_images")

'''
JSON
'''
class JSON:
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
                    print("\
    ERROR: JSON.updateProperty - did not update the json file. \
    Type of new value does not match the type of the property")
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
                    print("\
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


def getCurrentSectionNameWprefix():
    sectionPrefix = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.sections_prefix_ID)
    currSection = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.currSection_ID)
    return sectionPrefix + "_" + currSection

def getCurrentSectionPdfName():
    return getCurrentSectionNameWprefix() + "_" + "main.myPDF"


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


def getListOfBooks():
    booksPathsDict = Settings.readProperty(Settings.PubProp.booksPaths_ID)
    return booksPathsDict.keys()


def getAllRunningApps():
    #get all the running applications
    workspace = NSWorkspace.sharedWorkspace()
    activeApps = workspace.runningApplications()
    return activeApps


def getWindowsFromApp(app):
    # if app.isActive():
    options = Quartz.kCGWindowListOptionOnScreenOnly
    return Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)


def getOwnersName_windowID_ofApp(appName, windowIdentifier = ""):
    activeApps = getAllRunningApps()
    
    app = [i for i in activeApps if appName in str(i).lower()][0]
    if app == None :
        print ("getOwnersName_windowID_ofApp - the app was not found")
        return None, None
    
    windowList = getWindowsFromApp(app)
    windowIndex = 1
    
    for window in windowList:
        if window["kCGWindowOwnerName"] == app.localizedName():
            if windowIdentifier in window["kCGWindowName"]:
                ownerName = str(window["kCGWindowOwnerName"])
                windowID = str(windowIndex)

                return ownerName, windowID
            windowIndex += 1
    
    print("getOwnersName_windowID_ofApp - window was not found")
    return None, None


def getpageOfcurrentDoc():

    activeApps = getAllRunningApps()
    
    app = [i for i in activeApps if Settings.skim_ID in str(i).lower()][0]
    if app == None :
        print ("getpageOfcurrentDoc - skim was not found")
        return -1
    
    windowList = getWindowsFromApp(app)
    currChapter = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.currSection_ID)
    
    for window in windowList:
        if window["kCGWindowOwnerName"] == app.localizedName():
            if currChapter + "_main.myPDF" in window["kCGWindowName"]:
                windowName = str(window["kCGWindowName"])
                pageNum = windowName.split("page ")[1]
                pageNum = pageNum.split(" ")[0]
                return pageNum


def getCurrSecImIdx():
    currSectionPath = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.currSection_ID)
    imIndex_ID = fsm.Wr.SectionInfoStructure.PubProp.imIndex_ID
    return fsm.Wr.SectionInfoStructure.readProperty(currSectionPath, imIndex_ID)


'''
working with Settings
'''
class Settings:

    class PubProp:
        #current settings
        currState_ID = "currentState"
        currBookPath_ID = currState_ID + "_BookPath"
        currBookName_ID = currState_ID + "_BookName"
        currLayout_ID = currState_ID + "_Layout"        
        currScreenshotLocation_ID = currState_ID + "_ScreenshotLocation"        

        wholeBook_ID= "whole_book"

        booksPaths_ID = "booksPaths"
    
    #common
    booksSettingsName = "booksProcessingSettings.json"
    
    #app IDs
    class _appsIDs:
        skim_ID = "skim"
        vsCode_ID = "Code"
        finder_ID = "Finder"

    class UI:
        showMainWidgetsNext = False

    #layouts
    #NOTE: it is used to cut the layout class name
    layoutsList = ["Section", "Main", "WholeVSCode"]
    layoutClassToken = "Layout"
    currLayout = ""
    mon_windth, mon_height  = getMonitorSize()


    #paths # need to be imported from bookInfoStructuere
    relToSubchapters_Path = "/subchapters/"

    class Layout:
        def getCurrLayoutClass():
            layoutStr = Settings.readProperty(Settings.PubProp.currLayout_ID)
            layouts_main = sys.modules["layouts_main"]
            return getattr(layouts_main, layoutStr + Settings.layoutClassToken)

    class Book:
        @classmethod
        def addNewBook(cls, bookName, bookPath):
            cls.setCurrentBook(bookName, bookPath)
            booksPaths = Settings.readProperty(Settings.PubProp.booksPaths_ID)
            booksPaths[bookName] = bookPath
            Settings.updateProperty(Settings.PubProp.booksPaths_ID, booksPaths)

        def setCurrentBook(bookName, bookPath):
            Settings.updateProperty(Settings.PubProp.currBookPath_ID, bookPath)
            Settings.updateProperty(Settings.PubProp.currBookName_ID, bookName)
        
        @classmethod
        def getWholeBookPath(cls):
            path = os.path.join(Settings.readProperty(Settings.PubProp.currBookPath_ID),
                            fsm.Wr.OriginalMaterialStructure.originalMaterialBaseRelPath,
                            Settings.PubProp.wholeBook_ID + ".pdf")
            print(path)
            return path

        def getCurrBookFolderPath():
            return Settings.readProperty(Settings.PubProp.currBookPath_ID)
        
        @classmethod
        def getCurrentBookFolderName(cls):
            return cls.getCurrBookFolderPath().split("/")[-1]
    
    @classmethod
    def getSettingsFileFilepath(cls):
        return os.environ['BOOKS_SETTINGS_PATH'] + cls.booksSettingsName
    

    @classmethod
    def fromCurrChapterSettingToFinderChapterName(cls, currChapterSettingName):
        return "ch" + currChapterSettingName.split(".")[0]
    

    @classmethod 
    def readProperty(cls, propertyName):
        return JSON.readProperty(cls.getSettingsFileFilepath(), propertyName)
   

    @classmethod
    def updateProperty(cls, propertyName, newValue):
        JSON.updateProperty(cls.getSettingsFileFilepath(), propertyName, newValue)

