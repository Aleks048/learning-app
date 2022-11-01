import sys, os, json
from screeninfo import get_monitors
from AppKit import NSWorkspace
import Quartz

# import UI.widgets_collection as ui
import UI.widgets_messages as wm
import file_system.file_system_main as fs


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

def getCurrentSectionAbsDir():
    relFilepath = getCurrentSectionRelDir()
    bookPath = Settings.readProperty(Settings.PubProp.currBookPath_ID)
    return bookPath + "/" + relFilepath

def getCurrentSectionRelDir():
    currSec = fs.BookInfoStructure.readProperty(fs.BookInfoStructure.PubProp.currSection_ID)
    filepath = fs.BookInfoStructure.readProperty(currSec)["path"]
    bookpath = Settings.readProperty(Settings.PubProp.currBookPath_ID)

    relFilepath = filepath.replace(bookpath, "")
    relFilepath = "/".join(relFilepath.split("/")[:-1])
    return relFilepath

def getCurrentScreenshotRelDir():
    return  getCurrentSectionRelDir() + "/images/"

def getCurrentScreenshotAbsDir():
    return  getCurrentSectionAbsDir() + "/images/"

'''
JSON
'''
def readJSONfile(filePath):
    # print("readJSONfile - reading json file: " + filePath)
    with open(filePath, 'r') as f:
        outputList = json.loads(f.read())
        return outputList

def writeJSONfile(filePath, dataTowrite):
    # print("writeJSONfile - writing to json file: " + filePath)
    with open(filePath, 'w') as f:
        jsonObj = json.dumps(dataTowrite, indent=4)
        f.write(jsonObj)

def readJSONProperty(jsonFilepath, propertyName):
    jsonData = readJSONfile(jsonFilepath)
    
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

def updateJSONProperty(jsonFilepath, propertyName, newValue):
    # print("updateJSONProperty - updating property " + propertyName + " in settings file")
   
    def _updateProperty(jsonData, newValue):
        if propertyName in jsonData:
            if type(newValue) != type(jsonData[propertyName]):
                 print("ERROR: updateJSONProperty - did not update the json file. Type of new value does not match the type of the property")
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
    
    jsonData = readJSONfile(jsonFilepath)
    _updateProperty(jsonData, newValue)
    writeJSONfile(jsonFilepath, jsonData)


'''
manipulate dict
'''
def readDictProperty(dictToReadFrom, propertyName):
    if propertyName in dictToReadFrom:
        return dictToReadFrom[propertyName]
    for _, v in dictToReadFrom.items():
        if type(v) is list:
            for i in v:
                property = readDictProperty(i, propertyName)
                if property != None:
                    return property
        elif type(v) is dict:
            property = readDictProperty(v, propertyName)
            if property != None:
                return property

def updateDictProperty(dictToUpdate, propertyName, newValue):
    if propertyName in dictToUpdate:
        if type(newValue) != type(dictToUpdate[propertyName]):
                print("ERROR: updateJSONProperty - did not update the json file. Type of new value does not match the type of the property")
        else:
            dictToUpdate[propertyName] = newValue
    else:
        for k, v in dictToUpdate.items():
            if type(v) is list:
                for i in range(len(v)):
                    if v[i] is dict or v[i] is list:
                        updateDictProperty(v[i], propertyName, newValue)
            elif type(v) is dict:
                updateDictProperty(v, propertyName, newValue)





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


def getPositionsOfMarker(lines, marker):
    '''
    return a list of positions of a marker in lines
    '''
    positions = []
    for i in range(0, len(lines)):
        if marker in lines[i]:
            positions.append(i)
    return positions
            

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
    return "/".join(fp.split("/")[:-1])


def getPathToBooks():
    return os.getenv("BOOKS_ROOT_PATH")


def getListOfBooks():
    pathToBooks = getPathToBooks()
    return [i for i in os.listdir(pathToBooks) if i[:2]=="b_"]


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
    currChapter = fs.BookInfoStructure.readProperty(fs.BookInfoStructure.PubProp.currSection_ID)
    
    for window in windowList:
        if window["kCGWindowOwnerName"] == app.localizedName():
            if currChapter + "_main.pdf" in window["kCGWindowName"]:
                windowName = str(window["kCGWindowName"])
                pageNum = windowName.split("page ")[1]
                pageNum = pageNum.split(" ")[0]
                return pageNum

def getCurrSecImIdx():
    currSectionPath = fs.BookInfoStructure.readProperty(fs.BookInfoStructure.PubProp.currSection_ID)
    imIndex_ID = fs.SectionInfoStructure.PubProp.imIndex_ID
    return fs.SectionInfoStructure.readProperty(currSectionPath, imIndex_ID)


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
        showChapterWidgets = False

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
            return getPathToBooks() \
                +  Settings.readProperty(cls.getCurrentBookFolderName()) \
                + "/" + Settings.PubProp.wholeBook_ID \
                + "/" + Settings.PubProp.wholeBook_ID + ".pdf"

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
        return readJSONProperty(cls.getSettingsFileFilepath(), propertyName)
   

    @classmethod
    def updateProperty(cls, propertyName, newValue):
        updateJSONProperty(cls.getSettingsFileFilepath(), propertyName, newValue)


'''
chapters and subchapters data 
'''
class BookSettings:
    chaptersSettingsRelPath = "/bookInfo/bookInfo.json"
        

    class ChapterProperties:
        ch_ID = "ch"
        ch_name_ID = "_name"
        ch_latestSubchapter_ID = "_latestSubchapter"
        ch_startPage_ID = "_startPage"
        ch_imageIndex_ID = "_imIndex"
        ch_subchapters_ID = "_subSections"
        sec_sections_prefix_ID = "sections_prefix"

        @classmethod
        def getChapterNamePropertyID(cls, chapterNum):
            return cls.ch_ID + chapterNum + cls.ch_name_ID
        

        @classmethod
        def getChapterLatestSubchapterPropertyID(cls, chapterNum):
            return cls.ch_ID + chapterNum + cls.ch_latestSubchapter_ID
        

        @classmethod
        def getChapterStartPagePropertyID(cls, chapterNum):
            return cls.ch_ID + chapterNum + cls.ch_startPage_ID
        

        @classmethod
        def getChapterImIndexPropertyID(cls, chapterNum):
            return cls.ch_ID + chapterNum + cls.ch_imageIndex_ID
        

        @classmethod
        def getChapterSubchaptersPropertyID(cls, chapterNum):
            return cls.ch_ID + chapterNum + cls.ch_subchapters_ID


        @classmethod
        def _getEmptyChapter(cls, chNum):
            chString = BookSettings.ChapterProperties.ch_ID + chNum
            outChDict = {}
            outChDict[cls.getChapterNamePropertyID(chNum)] = ""
            outChDict[cls.getChapterLatestSubchapterPropertyID(chNum)] = ""
            outChDict[cls.getChapterStartPagePropertyID(chNum)] = ""
            outChDict[cls.getChapterImIndexPropertyID(chNum)] = "0"
            outChDict[cls.getChapterSubchaptersPropertyID(chNum)] = {}
            return chString, outChDict
        

        @classmethod
        def addChapter(cls, chNum, chName, chStartPage):
            if chNum != None:
                emptyChName, emptyChapter = cls._getEmptyChapter(chNum)
                jsonData = readJSONfile(BookSettings.getCurrBookChapterInfoJSONPath())
                if chName != None:
                    emptyChapter[cls.getChapterNamePropertyID(chNum)] = chName
                if chStartPage != None:
                    emptyChapter[cls.getChapterStartPagePropertyID(chNum)] = chStartPage
                
                if emptyChName not in jsonData:
                    jsonData[emptyChName] = emptyChapter
                    writeJSONfile(BookSettings.getCurrBookChapterInfoJSONPath(), jsonData)
                    
                    message = "created chapter: " \
                            + chNum + "\nwith Name: " \
                            + chName + "\nwith starting page: " + chStartPage
                    wm.ShowMessageMenu.createMenu(message)
                    print("addChapter - " + message)
                else:
                    message = "Did not create chapter: " \
                            + chNum \
                            + ". It is already in the data."
                    wm.ShowMessageMenu.createMenu(message)
                    print("addChapter - " + message)
            else:
                message = "Did not add chapter since the chapter num is empty."
                wm.ShowMessageMenu.createMenu(message)
                print("addChapter - " + message)
        

        @classmethod
        def removeChapter(cls, chNum):
            if chNum != None:
                jsonData = readJSONfile(BookSettings.getCurrBookChapterInfoJSONPath())
                if cls.ch_ID + chNum in jsonData:
                    jsonData.pop(cls.ch_ID + chNum)
                    writeJSONfile(BookSettings.getCurrBookChapterInfoJSONPath(), jsonData)
                    message = "removed chapter: " + chNum
                    ui.UIWidgets.showMessage(message)
                    print("removeChapter - " + message)
                else:
                    message = "Did not remove chapter: " + chNum + ". It was not in the chapter settings data."
                    ui.UIWidgets.showMessage(message)
                    print("removeChapter - " + message)
            else:
                message = "Did not remove chapter since the chapter num is empty."
                ui.UIWidgets.showMessage(message)
                print("removeChapter - " + message)


        @classmethod
        def getChapterName(cls, chapterNum):
            propertyName = cls.getChapterNamePropertyID(chapterNum)
            return readJSONProperty(BookSettings.getCurrBookChapterInfoJSONPath(),
                                    propertyName)


        @classmethod
        def getChapterLatestSubchapter(cls, chapterNum):
            propertyName = cls.getChapterLatestSubchapterPropertyID(chapterNum)
            return readJSONProperty(BookSettings.getCurrBookChapterInfoJSONPath(), 
                                    propertyName)


        @classmethod
        def getChapterName(cls, chapterNum):
            propertyName = cls.getChapterNamePropertyID(chapterNum)
            return readJSONProperty(BookSettings.getCurrBookChapterInfoJSONPath(), 
                                    propertyName)


        @classmethod
        def getCurrSectionImIndex(cls):
            sectionPath = fs.BookInfoStructure.readProperty(fs.BookInfoStructure.PubProp.currSection_ID)
            imIndex_ID = fs.SectionInfoStructure.PubProp.imIndex_ID
            imIndex = fs.SectionInfoStructure.readProperty(sectionPath, imIndex_ID)
            return imIndex
        

        @classmethod
        def getChapterStartPage(cls, chapterNum):
            propertyName = cls.ch_ID + chapterNum + cls.ch_startPage_ID
            return readJSONProperty(BookSettings.getCurrBookChapterInfoJSONPath(), 
                                    propertyName)
        

        @classmethod
        def updateChapterName(cls, chapterNum, chName):
            propertyName = cls.getChapterNamePropertyID(chapterNum)
            updateJSONProperty(BookSettings.getCurrBookChapterInfoJSONPath(), 
                                propertyName, 
                                chName)
            
            message = "Updated " + propertyName + " to: " + chName
            wm.ShowMessageMenu.createMenu(message)
            print("updateChapterName - " + message)
        

        @classmethod
        def updateChapterLatestSubchapter(cls, chapterNum, latestSubchapter):
            propertyName = cls.getChapterLatestSubchapterPropertyID(chapterNum)
            updateJSONProperty(BookSettings.getCurrBookChapterInfoJSONPath(), 
                                propertyName, 
                                latestSubchapter)
            
            message = "Updated " + propertyName + " to: " + latestSubchapter
            # ui.UIWidgets.showMessage(message)
            print("updateChapterName - " + message)
        

        @classmethod
        def updateChapterStartPage(cls, chapterNum, chStartPage):
            propertyName = cls.ch_ID + chapterNum + cls.ch_startPage_ID
            updateJSONProperty(BookSettings.getCurrBookChapterInfoJSONPath(), 
                                propertyName, 
                                chStartPage)  

            message = "Updated " + propertyName + " to: " + chStartPage
            wm.ShowMessageMenu.createMenu(message)
            print("updateChapterStartPage - " + message)
        

        @classmethod
        def updateChapterImageIndex(cls, chapterNum, chimIndex):
            propertyName = cls.ch_ID + chapterNum + cls.ch_imageIndex_ID
            updateJSONProperty(BookSettings.getCurrBookChapterInfoJSONPath(), 
                                propertyName, 
                                chimIndex)  

            message = "Updated " + propertyName + " to: " + chimIndex
            # ui.UIWidgets.showMessage(message)
            print("updateChapterImageIndex - " + message)


    class SubchaptersProperties:
        subch_ID = "subch_"
        subch_name_ID = "_name"
        subch_startPage_ID = "_startPage"

        @classmethod
        def _getEmptySubchapter(cls, subchNum):
            subchString = BookSettings.SubchaptersProperties.subch_ID + subchNum
            outSubchDict = {}
            outSubchDict[cls.getSubchapterNamePropertyID(subchNum)] = ""
            outSubchDict[cls.getSubchapterStartPagePropertyID(subchNum)] = ""
            return subchString, outSubchDict

        @classmethod
        def addSubchapter(cls, chNum, subchNum, subchName, subchStartPage):
            chString = BookSettings.ChapterProperties.ch_ID + chNum
            if chNum != None and subchNum != None:
                emptySubchName, emptySubchapter = cls._getEmptySubchapter(subchNum)
                if subchName != None:
                    emptySubchapter[cls.getSubchapterNamePropertyID(subchNum)] = subchName
                if subchStartPage != None:
                    emptySubchapter[cls.getSubchapterStartPagePropertyID(subchNum)] = subchStartPage
                
                jsonData = readJSONfile(BookSettings.getCurrBookChapterInfoJSONPath())
                chString = BookSettings.ChapterProperties.ch_ID + chNum
                if chString in jsonData:
                    if emptySubchName not in jsonData[chString][chString + BookSettings.ChapterProperties.ch_subchapters_ID]:
                        jsonData[BookSettings.ChapterProperties.ch_ID + chNum][chString + BookSettings.ChapterProperties.ch_subchapters_ID][emptySubchName] = emptySubchapter
                        writeJSONfile(BookSettings.getCurrBookChapterInfoJSONPath(), jsonData)
                        
                        message = "Created subchapter: "\
                                    + subchNum + "\nwith Name: " \
                                    + subchName + "\nwith starting page: " \
                                    + subchStartPage
                        wm.ShowMessageMenu.createMenu(message)
                        print("addSubchapter - " + message)
                    else:
                        message = "Did not create subchapter: " + subchNum\
                                    + ". It is already in the data."
                        wm.ShowMessageMenu.createMenu(message)
                        print("addSubchapter - " + message)
                else:
                    message = "Did not add subchchapter since the chapter does not exist."
                    wm.ShowMessageMenu.createMenu(message)
                    print("addSubchapter - " + message)
            else: #subch or ch are None
                if chNum == None:
                    message = "Did not add subchchapter since the chapter num is empty."
                    wm.ShowMessageMenu.createMenu(message)
                    print("addSubchapter - " + message)
                else:
                    # subchNum is None
                    message = "Did not add subchchapter since the subchNum num is empty."
                    wm.ShowMessageMenu.createMenu(message)
                    print("addSubchapter - " + message)
        

        @classmethod
        def removeSubchapter(cls, chNum, subchNum):
            chString = BookSettings.ChapterProperties.ch_ID + chNum
            if chNum != None and subchNum != None:
                jsonData = readJSONfile(BookSettings.getCurrBookChapterInfoJSONPath())
                if chString in jsonData:
                    if cls.subch_ID + subchNum in  jsonData[chString][BookSettings.ChapterProperties.getChapterSubchaptersPropertyID(chNum)]:
                            jsonData[chString][BookSettings.ChapterProperties.getChapterSubchaptersPropertyID(chNum)].pop(cls.subch_ID + subchNum)
                            writeJSONfile(BookSettings.getCurrBookChapterInfoJSONPath(), jsonData)
                            message = "removed subchapter: " + subchNum
                            wm.ShowMessageMenu.createMenu(message)
                            print("removeChapter - " + message)
                    else:
                        message = "Did not remove subchapter: " + subchNum + ". It was not in the chapter settings data."
                        wm.ShowMessageMenu.createMenu(message)
                        print("removeSubchapter - " + message)
                else:
                    message = "Did not remove subchapter: " + subchNum + ". Chapter was not in the chapter settings data."
                    wm.ShowMessageMenu.createMenu(message)
                    print("removeSubhcapter - " + message)
            else:
                if (chNum == None):
                    message = "Did not remove chapter since the chapter num is empty."
                else: #subch is None
                    message = "Did not remove chapter since the subchapter num is empty."
                wm.ShowMessageMenu.createMenu(message)
                print("removeSubchapter - " + message)


        @classmethod
        def updateSubchapterName(cls, subchapterNum, subchName):
            propertyName = cls.subch_ID + subchapterNum + cls.subch_name_ID
            updateJSONProperty(BookSettings.getCurrBookChapterInfoJSONPath(), 
                                propertyName, 
                                subchName)

            message = "Updated " + propertyName + " to: " + subchName
            wm.ShowMessageMenu.createMenu(message)
            print("updateSubchapterName - " + message)
        
        
        @classmethod
        def getSubchapterStartPage(cls, subchapterNum):
            propertyName = cls.subch_ID + subchapterNum + cls.subch_startPage_ID
            readJSONProperty(BookSettings.getCurrBookChapterInfoJSONPath(), 
                            propertyName)
        

        @classmethod
        def updateSubchapterStartPage(cls, subchapterNum, subchStartPage):
            propertyName = cls.subch_ID + subchapterNum + cls.subch_startPage_ID
            updateJSONProperty(BookSettings.getCurrBookChapterInfoJSONPath(), 
                                propertyName, 
                                subchStartPage)  

            message = "Updated " + propertyName + " to: " + subchStartPage
            wm.ShowMessageMenu.createMenu(message)
            print("updateSubchapterStartPage - " + message)
        

        @classmethod
        def getSubchapterNamePropertyID(cls, subchapterNum):
            return cls.subch_ID + subchapterNum + cls.subch_name_ID
        
        
        @classmethod
        def getSubchapterStartPagePropertyID(cls, subchapterNum):
            return cls.subch_ID + subchapterNum + cls.subch_startPage_ID


        @classmethod
        def getSubchapterName(cls, subchapterNum):
            propertyName = cls.subch_ID + subchapterNum + cls.subch_name_ID
            readJSONProperty(BookSettings.getCurrBookChapterInfoJSONPath(), 
                            propertyName)
    

    @classmethod 
    def getCurrBookChapterInfoJSONPath(cls):
        currBookName = Settings.readProperty(Settings.PubProp.currBookName_ID)
        bookFolderPath = Settings.readProperty(Settings.PubProp.currBookPath_ID)
        return cls._getBookChapterInfoJSONPath(bookFolderPath)
    

    @classmethod
    def _getBookChapterInfoJSONPath(cls, bookFolderPath):
        return bookFolderPath + cls.chaptersSettingsRelPath


    @classmethod
    def readProperty(cls, property):
        return readJSONProperty(cls.getCurrBookChapterInfoJSONPath(), property)
    
    # @classmethod
    # def updateProperty(cls, property, value):
    #     return updateJSONProperty(cls.getCurrBookChapterInfoJSONPath(), property, value)

