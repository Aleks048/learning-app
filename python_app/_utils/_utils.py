from asyncore import read
from dataclasses import dataclass
from genericpath import isfile
import sys, os, json
from time import sleep
import tkinter as tk
from tkinter import messagebox
import tkinter
from typing import Set
from webbrowser import get
from layouts import layouts_main
from screeninfo import get_monitors

from threading import Thread

def getMonitorSize():
    for m in get_monitors():
       return(m.width,m.height)

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

def getCurrentScreenshotDir():
    return Settings.getBookFolderPath(Settings.readProperty(Settings.currBookName_ID)) + "/" \
        + Settings.readProperty(Settings.currChapter_ID) + "/"\
        + Settings.readProperty(Settings.currChapter_ID) + "_images/"

# def createJSONProperty(jsonFilepath, propertyPath):
#     propertyPathList = propertyPath.split(".")
#     propertyName = propertyPathList[0]
#     property = readJSONProperty(jsonFilepath, propertyName)
#     if property == None:
#         print("hi")
#     jsonData = readJSONfile(jsonFilepath)


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

def readOpenFile(file):
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


def getGetExcercisesImagesPath(callerFilepath):
    '''
    get excersises images path
    '''
    global exercisesImagesRelPath
    callerExcerciseImagesDirectory  = filePathToParentDir(callerFilepath) + exercisesImagesRelPath[1:]

def getPathToBooks():
    return os.getenv("BOOKS_ROOT_PATH")

def getListOfBooks():
    pathToBooks = getPathToBooks()
    return [i for i in os.listdir(pathToBooks) if i[:2]=="b_"]


'''
working with Settings
'''
class Settings:
    #current settings
    currSettings_ID = "currentSettings"
    currBookPath_ID = "currentBookPath"
    currBookName_ID = "currentBookFolderName"
    wholeBook_ID= "whole_book"
    currChapterFull_ID= "currChapterFull"
    currChapter_ID= "currChapter"
    currPage_ID = "currentPage"

    #image generation
    currImageID_ID = "currImageID"
    currImageName_ID = "currImageName"
    currLinkName_ID = "currLinkName"
    
    #common
    booksSettingsName = "booksProcessingSettings.json"
    
    #app IDs
    skim_ID = "skim"
    vsCode_ID = "Code"
    finder_ID = "Finder"

    #layouts
    layouts_ID = "Layouts"
    #NOTE: it is used to cut the layout class name
    layoutClass_ID = "Layout"
    currLayout = ""
    mon_windth, mon_height  = getMonitorSize()


    #paths
    relToSubchapters_Path = "/subchapters/"
    
    @classmethod
    def getWholeBookPath(cls):
        return getPathToBooks() +  cls.readProperty(cls.currBookName_ID) + "/" + cls.wholeBook_ID + "/" + cls.wholeBook_ID + ".pdf"
    def getBookFolderPath(bookName):
        return os.environ['BOOKS_ROOT_PATH'] + "/" + bookName
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
Class to store the widgets required for the menus
'''
class UIWidgets:
    showChapterWidgets = False

    entryWidget_ID = "ETR"

    listOfLayouts = Settings.readProperty(Settings.layouts_ID)
    listOfLayoutClasses = [getattr(layouts_main, layoutName + Settings.layoutClass_ID) for layoutName in listOfLayouts]

    #tk primvars
    class tkVariables:
        needRebuild = None
        buttonText = None
        createTOCVar = None
        TOCWithImageVar = None
        subchapter = None
        imageGenerationEntryText = None
        scrshotPath = None
        currCh = None
        currSubch = None

    def showMessage(text):
        # Create an instance of tkinter frame or window
        win = tk.Tk()

        # Set the size of the tkinter window
        win.geometry("350x350")

        
        messagebox.showinfo('Processing knoledge', text)

        win.bind("<Enter>", win.destroy())

        win.mainloop()

    def confirmationWindow(inText, onYesFunction, *args):
        root = tk.Tk()
        root.title("Confirmation")

        def onYesCallback():
            root.destroy()
            Thread(target=lambda: onYesFunction(*args)).start()
    
    
        l1=tk.Label(root, image="::tk::icons::question")
        l1.grid(row=0, column=0, pady=(7, 0), padx=(10, 30), sticky="e")
        l2=tk.Label(root,text= inText)
        l2.grid(row=0, column=1, columnspan=3, pady=(7, 10), sticky="w")
    
        b1=tk.Button(root,text="Yes",command = onYesCallback, width = 10)
        b1.grid(row=1, column=1, padx=(2, 35), sticky="e")
        b2=tk.Button(root,text="No",command=root.destroy,width = 10)
        b2.grid(row=1, column=2, padx=(2, 35), sticky="e")
        
        def onYesCallbackWrapper(e):
            onYesCallback()
        root.bind("<Return>", onYesCallbackWrapper)
        root.bind("<Escape>", lambda e: root.destroy())

        root.mainloop()
        

    '''
    hide all of the widgets in the mainWinRoot
    '''
    @classmethod
    def hideAllWidgets(cls, mainWinRoot):
        for e in mainWinRoot.winfo_children():
            # clear all entries
            if (cls.entryWidget_ID in e._name):
                if ("_imageGeneration_" not in e._name):
                    e.delete(0, 'end')
            e.grid_remove()

    @classmethod
    def showCurrentLayout(cls, mainWinRoot):
        l_Name = Settings.currLayout
        layoutClass = [i for i in cls.listOfLayoutClasses if i.__name__.replace(Settings.layoutClass_ID,"") == l_Name][0]
        layoutClass.set(mainWinRoot)
        UIWidgets.hideAllWidgets(mainWinRoot)

        for e in mainWinRoot.winfo_children():
            if layoutClass.__name__.lower() in e._name:
                if (cls.entryWidget_ID in e._name):
                    e.focus_set()
                e.grid()

    '''
    option menu to to get layouts
    '''
    @classmethod
    def getOptionsMenu_Layouts(cls, mainWinRoot, namePrefix = ""):
        def layoutOptionMenuCallback(layout_name_vatying):
            Settings.currLayout = layout_name_vatying.get()
            UIWidgets.showCurrentLayout(mainWinRoot)
        
        listOfLayouts = Settings.readProperty(Settings.layouts_ID)
        layout_name_vatying = tk.StringVar()
        layout_name_vatying.set(listOfLayouts[0])

        frame = tk.Frame(mainWinRoot, name = namePrefix.lower() + "_layouts_optionMenu", background="Blue")        
        layouts_optionMenu = tk.OptionMenu(frame, layout_name_vatying, *listOfLayouts, command= lambda x: layoutOptionMenuCallback(layout_name_vatying))
        
        layouts_optionMenu.grid(row=0, column=0)
        
        return frame

    '''
    button to open the current full text in skim
    '''
    def getButton_OpenFullBook(mainWinRoot):
        screenHalfWidth, screenHeight = getMonitorSize()
        screenHalfWidth = str(int(screenHalfWidth / 2))
        screenHeight = str(screenHeight)

        def openFullTextButtonCallback():
            wholeBookDimensions = ["0", "0", screenHalfWidth, screenHeight]
            layouts_main.openWholeBook([wholeBookDimensions[2], wholeBookDimensions[3]], [wholeBookDimensions[0], wholeBookDimensions[1]])
        
        openFullTextButtonText = tk.StringVar()
        openFullTextButtonText.set("Current book is :\n" +  Settings.readProperty(Settings.currBookName_ID))
        
        return tk.Button(mainWinRoot, name = "openFullBook_button", textvariable = openFullTextButtonText, width = 10, command = openFullTextButtonCallback)

    '''
    create a text widget with the current folder where the images are saved
    '''  
    class Screenshot:
        
        def getScreenshotLocation():
            if UIWidgets.tkVariables.scrshotPath.get() == "":
                return "Current screenshot dir: " + getCurrentScreenshotDir()
            else:
                return "Current screenshot dir: " + UIWidgets.tkVariables.scrshotPath.get()
        
        def setScreenshotLoaction():
            UIWidgets.tkVariables.scrshotPath.set(getCurrentScreenshotDir())

        @classmethod
        def getText_CurrentScreenshotDir(cls, mainWinRoot, namePref = ""):
            canvas= tk.Canvas(mainWinRoot,name = namePref.lower() + "_showCurrScreenshotLocation_text", width=520, height= 25)

            UIWidgets.tkVariables.scrshotPath = tk.StringVar()
            currScrshDir = UIWidgets.tkVariables.scrshotPath

            currScrshDir.set(cls.getScreenshotLocation())
            
            txt = canvas.create_text(30, 10, anchor="nw", text=currScrshDir.get())

            def on_change(varname, index, mode):
                canvas.itemconfigure(txt, text=cls.getScreenshotLocation())
            
            currScrshDir.trace_variable('w', on_change)

            return canvas

    class ChooseBookChapter:
        '''
        option menu to choose a book to open and work on
        '''
        @classmethod
        def getOptionsMenu_ChooseBook(cls, mainWinRoot, namePrefix = ""):
            def bookMenuChooseCallback(book_name):
                Settings.updateProperty(Settings.currBookPath_ID, getPathToBooks() + book_name.get() + "/" + Settings.wholeBook_ID + "/" + Settings.wholeBook_ID + ".pdf")

            default_book_name="Select a a book"

            '''
            functions that retrun options menus for choosing book
            '''
            book_name = tk.StringVar()
            book_name.set(default_book_name)

            # Create the list of books we have
            listOfBooksNames = getListOfBooks()

            frame = tk.Frame(mainWinRoot, name = namePrefix.lower() + "_chooseBook_optionMenu", background="Blue")
            book_menu = tk.OptionMenu(frame, book_name, *listOfBooksNames, command= lambda x: bookMenuChooseCallback(book_name))
            book_menu.grid(row=0, column = 0)
            return frame


        @classmethod
        def getOptionMenu_ChooseChapter(cls, mainWinRoot, namePrefix = ""):
            '''
            functions that retrun options menus for choosing chapter
            '''
            def chapterChoosingCallback(chapter):
                print("chapterChoosingCallback - switching to chapter: " + chapter.get())

                # chapterPath = getPathToBooks() + Settings.readProperty(Settings.currBookName_ID) + "/" + chapter.get()
                Settings.updateProperty(Settings.currChapter_ID , chapter.get())

                chapterImIndex = Chapters.ChapterProperties.getCurrChapterImIndex()
                UIWidgets.tkVariables.imageGenerationEntryText.set(chapterImIndex)

                UIWidgets.Screenshot.setScreenshotLoaction()
                
                subchaptersList = cls._getSubchaptersListForCurrChapter()
                cls._updateOptionMenuOptionsList(mainWinRoot, "_chooseSubchapter_optionMenu", subchaptersList)
                currSubchapter = Chapters.ChapterProperties.getChapterLatestSubchapter(Settings.readProperty(Settings.currChapter_ID)[2:])
                UIWidgets.tkVariables.subchapter.set(currSubchapter)
                Settings.updateProperty(Settings.currChapterFull_ID, subchaptersList[0])

                currLayoutClass = layouts_main.getCurrLayoutClass()
                currLayoutClass.pyAppHeight = mainWinRoot.winfo_height()
                currLayoutClass.set(mainWinRoot)
                layouts_main.moveWholeBookToChapter()

            chapter = tk.StringVar()
            chapter.set(Settings.readProperty(Settings.currChapter_ID))

            book_name = Settings.readProperty(Settings.currBookName_ID)

            pathToBooks = getPathToBooks()
            chaptersList = []
            chaptersList.extend([i for i in os.listdir(pathToBooks + "/" + book_name) if i[:2]=="ch"])
            chaptersList.sort(key=lambda x: -1 if x[2:]=="" else int(x[2:]))
            
            frame = tk.Frame(mainWinRoot, name = namePrefix.lower() + "_chooseChapter_optionMenu", background="Blue")
            chapter_menu = tk.OptionMenu(frame, chapter, *chaptersList, command= lambda x: chapterChoosingCallback(chapter))
            chapter_menu.grid(row = 0, column = 0)

            return frame

        def _updateOptionMenuOptionsList(mainWinRoot, menuID, newMenuOptions):

            def subchapterChoosingCallback(value):
                UIWidgets.tkVariables.subchapter.set(value)
                Chapters.ChapterProperties.updateChapterLatestSubchapter(Settings.readProperty(Settings.currChapter_ID)[2:],
                                                                        value)
                Settings.updateProperty(Settings.currChapterFull_ID, value)

            for e in mainWinRoot.winfo_children():
                if menuID in e._name:
                    for om in e.winfo_children():
                        om['menu'].delete(0, 'end')
                        for choice in newMenuOptions:
                            om['menu'].add_command(label=choice, 
                                                command= lambda value=choice: subchapterChoosingCallback(value))
                            UIWidgets.tkVariables.subchapter.set(newMenuOptions[0])

        def _getSubchaptersListForCurrChapter():
            pathToBooks = getPathToBooks()
            currChapter = Settings.readProperty(Settings.currChapter_ID)
            currBookName = Settings.readProperty(Settings.currBookName_ID)
            return [i[3:] for i in os.listdir(pathToBooks + "/" + currBookName + "/" + currChapter + "/" + Settings.relToSubchapters_Path) if "ch_" in i]
        
        @classmethod
        def getOptionMenu_ChooseSubchapter(cls, mainWinRoot, namePrefix = ""):
            def subchapterChoosingCallback(subchapter):
                Chapters.ChapterProperties.updateChapterLatestSubchapter(Settings.readProperty(Settings.currChapter_ID)[2:],
                                                                        subchapter.get())
                Settings.updateProperty(Settings.currChapterFull_ID, subchapter.get())
            
            UIWidgets.tkVariables.subchapter  = tk.StringVar()
            subchapter = UIWidgets.tkVariables.subchapter
            subchapter.set(Settings.readProperty(Settings.currChapterFull_ID))
            
            subchaptersList = cls._getSubchaptersListForCurrChapter()

            frame = tk.Frame(mainWinRoot, name = namePrefix.lower() + "_chooseSubchapter_optionMenu", background="Blue")
            subchapter_menu = tk.OptionMenu(frame, subchapter, *subchaptersList, command= lambda x: subchapterChoosingCallback(subchapter))
            subchapter_menu.grid(row = 0, column = 0)
            return frame
    

    def getCheckboxes_TOC(mainWinRoot, namePrefix = ""):
        UIWidgets.tkVariables.createTOCVar = tk.IntVar()
        UIWidgets.tkVariables.createTOCVar.set(1)
        createTOC_CB = tk.Checkbutton(mainWinRoot, name = namePrefix.lower() + "_create_toc", text = "TOC cr",
                                    variable = UIWidgets.tkVariables.createTOCVar, onvalue = 1, offvalue = 0)
        UIWidgets.tkVariables.TOCWithImageVar = tk.IntVar()
        TOCWithImage_CB = tk.Checkbutton(mainWinRoot, name = namePrefix.lower() + "_toc_w_image",  text = "TOC w i",
                                    variable = UIWidgets.tkVariables.TOCWithImageVar, onvalue = 1, offvalue = 0)
        return createTOC_CB, TOCWithImage_CB

    def getImageGenerationRestart_BTN(mainWinRoot, namePrefix = ""):
        def restartBTNcallback():
            UIWidgets.tkVariables.buttonText.set("imNum")
            chapterImIndex = Chapters.ChapterProperties.getCurrChapterImIndex()
            UIWidgets.tkVariables.imageGenerationEntryText.set(chapterImIndex)
        
        restart_BTN = tk.Button(mainWinRoot,
                                name = namePrefix.lower() + "_imageGenerationRestartBTN",
                                text= "restart", 
                                command = restartBTNcallback)
        return restart_BTN

    @classmethod
    def getAddImage_BTN(cls, mainWinRoot, prefixName = ""):
        def addImBTNcallback():
            currImID = str(int(Settings.readProperty(Settings.currImageID_ID)) - 1)
            currentSubchapter = Settings.readProperty(Settings.currChapterFull_ID)
            
            # screenshot
            imName = ""

            # get name of the image from the text field
            for w in mainWinRoot.winfo_children():
                if "_imageGeneration_" + cls.entryWidget_ID in w._name:
                    imName = w.get()
            
            extraImagePath = getCurrentScreenshotDir() \
                                + currImID + "_" + currentSubchapter \
                                + "_" + imName
            
            if os.path.isfile(extraImagePath + ".png"):
                def takeScreencapture(savePath):
                    os.system("screencapture -ix " + savePath)
                    UIWidgets.tkVariables.needRebuild.set(True)
                cls.confirmationWindow("The file exists. Overrite?", takeScreencapture, extraImagePath + ".png")
            else:
                os.system("screencapture -ix " + extraImagePath + ".png")
                UIWidgets.tkVariables.needRebuild.set(True)

            # update the content file
            marker = "THIS IS CONTENT id: " + currImID
            with open(TexFile._getCurrContentFilepath(), "r+") as f:
                contentLines = f.readlines()
                lineNum = [i for i in range(len(contentLines)) if marker in contentLines[i]][0]
                extraImagesMarker = "% \\EXTRA IMAGES END"
                while extraImagesMarker not in contentLines[lineNum]:
                    lineNum += 1
                outLines = contentLines[:lineNum]
                extraImageLine = "\
    \\\\\myStIm{" + extraImagePath + "}\n"
                outLines.append(extraImageLine)
                outLines.extend(contentLines[lineNum:])

                f.seek(0)
                f.writelines(outLines)
            
            TexFile._populateMainFile()
        
        return tk.Button(mainWinRoot, 
                        name = prefixName.lower() + "_imageGenerationAddImBTN",
                        text= "addIm",
                        command = addImBTNcallback)

    '''
    create entry and process button for image generation
    '''
    @classmethod
    def getTextEntryButton_imageGeneration(cls, mainWinRoot, prefixName = ""):
        cls.tkVariables.imageGenerationEntryText = tk.StringVar()
        imageProcessingETR = tk.Entry(mainWinRoot, 
                                    width = 8,
                                    textvariable =  cls.tkVariables.imageGenerationEntryText,
                                    name=prefixName.lower() + "_imageGeneration_" + cls.entryWidget_ID)

        chapterImIndex = Chapters.ChapterProperties.getCurrChapterImIndex()
        cls.tkVariables.imageGenerationEntryText.set(chapterImIndex)

        dataFromUser = [-1, -1, -1]
        UIWidgets.tkVariables.buttonText = tk.StringVar()

        def _storeInputDataAndChange(nextButtonName, f = lambda *args: None, i = 0):
            # NOTE: not sure what is going on but "dataFromUser" refused to clean 
            # so had to pass i to set the position explicitly and set it to [-1, -1, -1] before
            dataFromUser[i] = imageProcessingETR.get()
            f()
            UIWidgets.tkVariables.buttonText.set(nextButtonName)

        def _createImageScript():
            scriptFile = ""
            scriptFile += "#!/bin/bash\n"
            scriptFile += "\
conIDX=`grep -n \"% THIS IS CONTENT id: " + dataFromUser[0] +"\" \"" + TexFile._getCurrContentFilepath() + "\" | cut -d: -f1`\n"
            scriptFile += "\
tocIDX=`grep -n \"% THIS IS CONTENT id: " + dataFromUser[0] +"\" \"" + TexFile._getCurrTOCFilepath() + "\" | cut -d: -f1`\n"
            scriptFile += "\
if [ \"$conIDX\" != \"\" ]\n\
then\n\
osascript -  $conIDX <<EOF\n\
    on run argv\n\
        tell application \"code\"\n\
            activate\n\
            tell application \"System Events\"\n\
                keystroke \"1\" using {command down}\n\
                delay 0.1\n\
                keystroke \"g\" using {control down}\n\
                keystroke item 1 of argv + 20\n\
                keystroke return\n\
            end tell\n\
        end tell\n\
    end run\n\
EOF\n\
fi\n"
            scriptFile += "\
if [ \"$tocIDX\" != \"\" ]\n\
then\n\
osascript - $tocIDX <<EOF\n\
    on run argv\n\
        tell application \"code\"\n\
            activate\n\
            tell application \"System Events\"\n\
                keystroke \"2\" using {command down}\n\
                delay 0.1\n\
                keystroke \"g\" using {control down}\n\
                keystroke item 1 of argv\n\
                keystroke return\n\
            end tell\n\
        end tell\n\
    end run\n\
EOF\n\
fi\n"
            scriptFile += "osascript -e '\
tell application \"" + Settings.skim_ID + "\"\n\
    tell document \"" + Settings.readProperty(Settings.currChapterFull_ID) + "_main.pdf" + "\"\n\
        delay 0.1\n\
        go to page " + str(dataFromUser[0]) + "\n\
        end tell\n\
end tell'"
            return scriptFile

        def _createTexForTheProcessedImage():
            currentSubchapter = Settings.readProperty(Settings.currChapterFull_ID)

            extraImagePath = getCurrentScreenshotDir() \
                                + dataFromUser[0] + "_" + currentSubchapter \
                                + "_" + dataFromUser[1]

            # ADD CONTENT ENTRY TO THE PROCESSED CHAPTER
            with open(TexFile._getCurrContentFilepath(), 'a') as f:
                add_page = "\n\n\
% THIS IS CONTENT id: " + dataFromUser[0] + " \n\
    % TEXT BEFORE MAIN IMAGE\n\
    \n\
    \n\
    % TEXT BEFORE MAIN IMAGE\n\
    \\def\\imnum{" + dataFromUser[0] + "}\n\
    \\def\\linkname{" + dataFromUser[1] + "}\n\
    \\hyperdef{TOC}{\\linkname}{}\n\
    \myTarget{" + extraImagePath + "}{\\linkname\\imnum}\n\
    % TEXT AFTER MAIN IMAGE\n\
    \n\
    \n\
    % TEXT AFTER MAIN IMAGE\n\
    % \EXTRA IMAGES START\n\
    % \EXTRA IMAGES END\n\
    % TEXT AFTER EXTRA IMAGES\n\
    \n\
    \n\
    % TEXT AFTER EXTRA IMAGES\n\
    \\\\\\rule{\\textwidth}{0.4pt}\n\
    \\\\\\myGlLinks{\n\
        % \\myGlLink{}{}\n\
    }\n\
    \\\\Local links: \n\
    \\TOC\\newpage\n"
                
                f.write(add_page)

            if UIWidgets.tkVariables.createTOCVar.get():
                if UIWidgets.tkVariables.TOCWithImageVar.get():
                    # TOC ADD ENTRY WITH IMAGE
                    with open(TexFile._getCurrTOCFilepath(), 'a') as f:
                        toc_add_image = "\
% THIS IS CONTENT id: " + dataFromUser[0] + " \n\
\\mybox{\n\
    \\link[" + dataFromUser[0] + \
    "]{" + dataFromUser[1] + "} \\image[0.5]{" + \
    dataFromUser[0] + "_" + currentSubchapter + "_" + dataFromUser[1] + "}\n\
}\n\n\n"
                        f.write(toc_add_image)
                else:  
                    # TOC ADD ENTRY WITHOUT IMAGE
                    with open(TexFile._getCurrTOCFilepath(), 'a') as f:
                        toc_add_text = "\
% THIS IS CONTENT id: " + dataFromUser[0] + " \n\
\\mybox{\n\
    \\link[" + dataFromUser[0] + "]{" + dataFromUser[1] + "} \\textbf{!}\n\
}\n\n\n"
                        f.write(toc_add_text)
            

            #create a script to run on page change
            imageAnscriptPath = getCurrentScreenshotDir() + dataFromUser[0] + \
                                "_" + currentSubchapter + "_" + dataFromUser[1]

            # STOTE IMNUM, IMNAME AND LINK
            Settings.updateProperty(Settings.currImageID_ID, dataFromUser[0])
            Settings.updateProperty(Settings.currLinkName_ID, dataFromUser[1])
            
            # POPULATE THE MAIN FILE
            TexFile._populateMainFile()
            
            
            # take a screenshot
            if os.path.isfile(imageAnscriptPath + ".png"):
                def takeScreencapture(savePath):
                    os.system("screencapture -ix " + savePath + ".png")
                    UIWidgets.tkVariables.needRebuild.set(True)
                        #create a sript associated with image
                    with open(savePath + ".sh", "w+") as f:
                        for l in _createImageScript():
                            f.write(l)
                    os.system("chmod +x " + savePath + ".sh")
                    #update curr image index for the chapter
                    nextImNum = str(int(dataFromUser[0]) + 1)
                    Chapters.ChapterProperties.updateChapterImageIndex(Settings.readProperty(Settings.currChapter_ID)[2:],
                                                                        nextImNum)
                    Settings.updateProperty(Settings.currImageID_ID, nextImNum)
                    cls.tkVariables.imageGenerationEntryText.set(nextImNum)
                    UIWidgets.tkVariables.buttonText.set("imNum")
                
                cls.confirmationWindow("The file exists. Overrite?", takeScreencapture, imageAnscriptPath)
            else:
                os.system("screencapture -ix " + imageAnscriptPath + ".png")
                UIWidgets.tkVariables.needRebuild.set(True)
                #create a sript associated with image
                with open(imageAnscriptPath + ".sh", "w+") as f:
                    for l in _createImageScript():
                        f.write(l)
                os.system("chmod +x " + imageAnscriptPath + ".sh")
                #update curr image index for the chapter
                nextImNum = str(int(dataFromUser[0]) + 1)
                Chapters.ChapterProperties.updateChapterImageIndex(Settings.readProperty(Settings.currChapter_ID)[2:],
                                                                    nextImNum)
                Settings.updateProperty(Settings.currImageID_ID, nextImNum)
                cls.tkVariables.imageGenerationEntryText.set(nextImNum)

        buttonNamesToFunc = {"imNum": lambda *args: cls.tkVariables.imageGenerationEntryText.set(""),
                            "imLink":_createTexForTheProcessedImage}
        buttonNames = list(buttonNamesToFunc.keys())
       
        UIWidgets.tkVariables.buttonText.set(buttonNames[0])

        def buttonCallback():
            for i in range(len(buttonNames)):
                if buttonNames[i] == UIWidgets.tkVariables.buttonText.get():
                    _storeInputDataAndChange(buttonNames[(i+1)%len(buttonNames)], 
                                            buttonNamesToFunc[buttonNames[i]], i)
                    break

        processButton = tk.Button(mainWinRoot, 
                                name = prefixName.lower() + "_imageGeneration_processButton",
                                textvariable = UIWidgets.tkVariables.buttonText, 
                                command= buttonCallback)
        return [imageProcessingETR, processButton]

    def getShowProofs_BTN(mainWinRoot, prefixName = ""):
        showProofsVar = tk.StringVar()
        showProofsVar.set("Hide Proofs")
        def _changeProofsVisibility(hideProofs):
            with open(TexFile._getCurrContentFilepath(),"r") as conF:
                contentLines = conF.readlines()
            extraImagesStartToken = "% \EXTRA IMAGES START"
            extraImagesEndToken = "% \EXTRA IMAGES END"
            for i in range(len(contentLines)):
                if (extraImagesStartToken in contentLines[i]):
                    while (extraImagesEndToken not in contentLines[i]):
                        i += 1
                        line = contentLines[i]
                        if "proof" in line.lower():
                            if hideProofs:
                                contentLines[i] = line.replace("% ", "")
                            else:
                                contentLines[i] = "% " + line
                    break
            with open(TexFile._getCurrContentFilepath(),"w") as conF:
                _waitDummy = conF.writelines(contentLines)
        
        def getShowProofsCallBack():
            if showProofsVar.get() == "Show Proofs":
                showProofsVar.set("Hide Proofs")
                _changeProofsVisibility(True)
                Thread(target=TexFile.buildCurrentSubchapterPdf).start()
            elif showProofsVar.get() == "Hide Proofs":
                showProofsVar.set("Show Proofs")
                _changeProofsVisibility(False)
                Thread(target=TexFile.buildCurrentSubchapterPdf).start()
        
        return tk.Button(mainWinRoot, 
                        name = prefixName.lower() + "_showProofsBTN",
                        textvariable = showProofsVar,
                        command = getShowProofsCallBack)

    def getSaveImage_BTN(mainWinRoot, prefixName = ""):
        def saveImageCallBack():
            _waitDummy = os.system("osascript -e '\
            tell application \"Preview\" to save the front document\n\
            tell application \"System Events\" to tell process \"Preview\"\n\
                tell front window \n\
                    click button 1\n\
	            end tell\n\
            end tell\
            '")
            TexFile.buildCurrentSubchapterPdf()
        return tk.Button(mainWinRoot, 
                        name = prefixName.lower() + "_saveImgBTN",
                        text = "saveIM",
                        command = saveImageCallBack)

    '''
    chapters menu widgets
    '''
    @classmethod
    class Chapters:
        chaptersPrefix = "chaptersID"

        @classmethod
        def setChaptersUI(cls, mainWinRoot):
            chooseChapter_MenusBtn = cls.getButton_chooseChaptersMenusAndBack(mainWinRoot, cls.chaptersPrefix)
            chooseChapter_MenusBtn.grid(row = 2, column = 3)
            entry_setChapterName, button_setChapterName = cls.getWidgets_setChapterName(mainWinRoot,  cls.chaptersPrefix)
            entry_setChapterName.grid(row = 0, column = 0)
            button_setChapterName.grid(row = 0, column = 1)
            entry_setChapterStartPage, button_setChapterStartPage = cls.getWidgets_setChapterStartPage(mainWinRoot,  cls.chaptersPrefix)
            entry_setChapterStartPage.grid(row = 1, column = 0)
            button_setChapterStartPage.grid(row = 1, column = 1)
            entry_setSubchapterName, button_setSubchapterName = cls.getWidgets_setSubchapterName(mainWinRoot,  cls.chaptersPrefix)
            entry_setSubchapterName.grid(row = 0, column = 2)
            button_setSubchapterName.grid(row = 0, column = 3)
            entry_setSubchapterStartpage, button_setSubchapterStartPage = cls.getWidgets_setSubchapterStartPage(mainWinRoot,  cls.chaptersPrefix)
            entry_setSubchapterStartpage.grid(row = 1, column = 2)
            button_setSubchapterStartPage.grid(row = 1, column = 3)
            
            UIWidgets.tkVariables.currCh = tk.StringVar()
            UIWidgets.tkVariables.currSubch = tk.StringVar()
            currCh_ETR, currSubch_ETR = cls.getEntries_currChAndSubchapter(mainWinRoot, cls.chaptersPrefix)
            currCh_ETR.grid(row = 2, column = 0, sticky = tk.N)
            currSubch_ETR.grid(row = 2, column = 2, sticky = tk.N)


            addCh_BTN = cls.getButton_createNewChapter(mainWinRoot, cls.chaptersPrefix)
            removeCh_BTN = cls.getButton_removeChapter(mainWinRoot, cls.chaptersPrefix)
            addCh_BTN.grid(row = 2, column = 0,sticky = tk.W)
            removeCh_BTN.grid(row = 2, column = 0, sticky = tk.E)
            
            addSubch_BTN = cls.getButton_createNewSubchapter(mainWinRoot, cls.chaptersPrefix)
            removeSubch_BTN = cls.getButton_removeSubchapter(mainWinRoot, cls.chaptersPrefix)
            addSubch_BTN.grid(row = 2, column = 2,sticky = tk.W)
            removeSubch_BTN.grid(row = 2, column = 2,sticky = tk.E)

        @classmethod
        def getButton_chooseChaptersMenusAndBack(cls, mainWinRoot, prefixName = ""):
            def chooseChaptersMenusAndBackCallback():
                # hide all of the menus
                UIWidgets.hideAllWidgets(mainWinRoot)

                if UIWidgets.showChapterWidgets:
                    mainWinRoot.columnconfigure(0, weight = 1)
                    mainWinRoot.columnconfigure(1, weight = 3)
                    mainWinRoot.columnconfigure(2, weight = 1)
                    mainWinRoot.columnconfigure(3, weight = 3)
                    
                    for w in mainWinRoot.winfo_children():
                        if cls.chaptersPrefix.lower() in w._name:
                            w.grid()
                    chooseChapter_MenusBtn_Label.set("chapters")
                    UIWidgets.showChapterWidgets = not UIWidgets.showChapterWidgets
                else:
                    mainWinRoot.columnconfigure(0, weight = 1)
                    mainWinRoot.columnconfigure(1, weight = 1)
                    mainWinRoot.columnconfigure(2, weight = 1)
                    mainWinRoot.columnconfigure(2, weight = 0)
                    UIWidgets.showCurrentLayout(mainWinRoot)  
                    chooseChapter_MenusBtn_Label.set("layout") 
                    UIWidgets.showChapterWidgets = not UIWidgets.showChapterWidgets

            
            # show getBack Button
            chooseChapter_MenusBtn_Label = tk.StringVar()
            chooseChapter_MenusBtn_Label.set("chapters") 
            chooseChapter_MenusBtn = tk.Button(mainWinRoot, name = prefixName.lower() + "_chooseChapterLayoutBtn", textvariable = chooseChapter_MenusBtn_Label, command = chooseChaptersMenusAndBackCallback)
            
            return chooseChapter_MenusBtn

        @classmethod
        def getEntries_currChAndSubchapter(cls, mainWinRoot, prefixName = ""):
            currCh_ETR = tk.Entry(mainWinRoot, width = 5, textvariable = UIWidgets.tkVariables.currCh, name = prefixName.lower() +  "_setCurrChapter_" + UIWidgets.entryWidget_ID)
            currSubch_ETR = tk.Entry(mainWinRoot, width = 5, textvariable = UIWidgets.tkVariables.currSubch, name = prefixName.lower() +  "_setCurrSubchapter_" + UIWidgets.entryWidget_ID)
            return currCh_ETR, currSubch_ETR

        @classmethod
        def getWidgets_setChapterName(cls, mainWinRoot, prefixName = ""):
            entry_setChapterName = tk.Entry(mainWinRoot, name = prefixName.lower() +  "_setChapterName_" + UIWidgets.entryWidget_ID)
            button_setChapterName = tk.Button(mainWinRoot, name = prefixName.lower() +  "_setChapterNameBTN", text="setChapterName", command = lambda *args: Chapters.ChapterProperties.updateChapterName(UIWidgets.tkVariables.currCh.get(), entry_setChapterName.get()))
            return entry_setChapterName, button_setChapterName            

        @classmethod
        def getWidgets_setChapterStartPage(cls, mainWinRoot, prefixName = ""):
            entry_setChapterStartPage = tk.Entry(mainWinRoot, name = prefixName.lower() +  "_setChapterStartPage_" + UIWidgets.entryWidget_ID)
            button_setChapterStartPage = tk.Button(mainWinRoot, name = prefixName.lower() + "_setChapterStartPageBTN", text="setChapterStartPage", command = lambda *args: Chapters.ChapterProperties.updateChapterStartPage(UIWidgets.tkVariables.currCh.get(), entry_setChapterStartPage.get()))
            return entry_setChapterStartPage, button_setChapterStartPage 

        @classmethod
        def getWidgets_setSubchapterName(cls, mainWinRoot, prefixName = ""):
            entry_setSubchapterName = tk.Entry(mainWinRoot, name = prefixName.lower() + "_setSubchapterName_" + UIWidgets.entryWidget_ID)
            button_setSubchapterName = tk.Button(mainWinRoot, name = prefixName.lower() + "_setSubchapterNameBTN", text="setSubhapterName", command = lambda *args: Chapters.SubchaptersProperties.updateSubchapterName(UIWidgets.tkVariables.currSubch.get(), entry_setSubchapterName.get()))
            return entry_setSubchapterName, button_setSubchapterName

        @classmethod
        def getWidgets_setSubchapterStartPage(cls, mainWinRoot, prefixName = ""):
            entry_setSubchapterStartpage = tk.Entry(mainWinRoot, name = prefixName.lower() + "_setSubchapterStartPage_" + UIWidgets.entryWidget_ID)
            button_setSubchapterStartPage = tk.Button(mainWinRoot, name = prefixName.lower() + "_setSubchapterStartPageBTN", text="setSubhapterStartName", command = lambda *args : Chapters.SubchaptersProperties.updateSubchapterStartPage(UIWidgets.tkVariables.currSubch.get(), entry_setSubchapterStartpage.get()))
            return entry_setSubchapterStartpage, button_setSubchapterStartPage

        @classmethod
        def getButton_createNewChapter(cls, mainWinRoot, prefixName = ""):
            def createNewChapterBTNcallback():
                chNum = None
                chName = None
                chStartPage = None
                for e in mainWinRoot.winfo_children():
                    if  "_setCurrChapter_" + UIWidgets.entryWidget_ID in e._name:
                        chNum = e.get()
                    elif "_setChapterName_" + UIWidgets.entryWidget_ID in e._name:
                        chName = e.get()
                    elif "_setChapterStartPage_" + UIWidgets.entryWidget_ID in e._name:
                        chStartPage = e.get()
                Chapters.ChapterProperties.addChapter(chNum, chName, chStartPage)
            
            return tk.Button(mainWinRoot, name = prefixName.lower() + "_createNewChapterBTN", text="New", command = createNewChapterBTNcallback)
        
        @classmethod
        def getButton_removeChapter(cls, mainWinRoot, prefixName = ""):
            def removeBTNcallback():
                chNum = None
                for e in mainWinRoot.winfo_children():
                    if  "_setCurrChapter_" + UIWidgets.entryWidget_ID in e._name:
                        chNum = e.get()
                        break
                Chapters.ChapterProperties.removeChapter(chNum)
            
            return tk.Button(mainWinRoot, name = prefixName.lower() + "_removeChapterBTN", text="Del", command = removeBTNcallback)
        
        @classmethod
        def getButton_createNewSubchapter(cls, mainWinRoot, prefixName = ""):
            def createNewChapterBTNcallback():
                chNum = None
                subchNum = None
                subchName = None
                subchStartPage = None
                for e in mainWinRoot.winfo_children():
                    if  "_setCurrSubchapter_" + UIWidgets.entryWidget_ID in e._name:
                        subchNum = e.get()
                        chNum = subchNum.split(".")[0]
                    elif "_setSubchapterName_" + UIWidgets.entryWidget_ID in e._name:
                        subchName = e.get()
                    elif "_setSubchapterStartPage_" + UIWidgets.entryWidget_ID in e._name:
                        subchStartPage = e.get()
                Chapters.SubchaptersProperties.addSubchapter(chNum, subchNum, subchName, subchStartPage)
            
            return tk.Button(mainWinRoot, name = prefixName.lower() + "_createNewSubchapterBTN", text="New", command = createNewChapterBTNcallback)

        @classmethod
        def getButton_removeSubchapter(cls, mainWinRoot, prefixName = ""):
            def removeBTNcallback():
                chNum = None
                for e in mainWinRoot.winfo_children():
                    if  "_setCurrSubchapter_" + UIWidgets.entryWidget_ID in e._name:
                        subchNum = e.get()
                        chNum = subchNum.split(".")[0]
                Chapters.SubchaptersProperties.removeSubchapter(chNum, subchNum)
            
            return tk.Button(mainWinRoot, name = prefixName.lower() + "_removeSubchapterBTN", text="Del", command = removeBTNcallback)


'''
chapters and subchapters data 
'''
class Chapters:
    chaptersSettingsRelPath = "/bookInfo/chaptersInfo.json"

    class ChapterProperties:
        ch_ID = "ch"
        ch_name_ID = "_name"
        ch_latestSubchapter_ID = "_latestSubchapter"
        ch_startPage_ID = "_startPage"
        ch_imageIndex_ID = "_imIndex"
        ch_subchapters_ID = "_subChapters"

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
            chString = Chapters.ChapterProperties.ch_ID + chNum
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
                jsonData = readJSONfile(Chapters.getCurrBookChapterInfoJSONPath())
                if chName != None:
                    emptyChapter[cls.getChapterNamePropertyID(chNum)] = chName
                if chStartPage != None:
                    emptyChapter[cls.getChapterStartPagePropertyID(chNum)] = chStartPage
                
                if emptyChName not in jsonData:
                    jsonData[emptyChName] = emptyChapter
                    writeJSONfile(Chapters.getCurrBookChapterInfoJSONPath(), jsonData)
                    
                    message = "created chapter: " + chNum + "\nwith Name: " + chName + "\nwith starting page: " + chStartPage
                    UIWidgets.showMessage(message)
                    print("addChapter - " + message)
                else:
                    message = "Did not create chapter: " + chNum + ". It is already in the data."
                    UIWidgets.showMessage(message)
                    print("addChapter - " + message)
            else:
                message = "Did not add chapter since the chapter num is empty."
                UIWidgets.showMessage(message)
                print("addChapter - " + message)
        
        @classmethod
        def removeChapter(cls, chNum):
            if chNum != None:
                jsonData = readJSONfile(Chapters.getCurrBookChapterInfoJSONPath())
                if cls.ch_ID + chNum in jsonData:
                    jsonData.pop(cls.ch_ID + chNum)
                    writeJSONfile(Chapters.getCurrBookChapterInfoJSONPath(), jsonData)
                    message = "removed chapter: " + chNum
                    UIWidgets.showMessage(message)
                    print("removeChapter - " + message)
                else:
                    message = "Did not remove chapter: " + chNum + ". It was not in the chapter settings data."
                    UIWidgets.showMessage(message)
                    print("removeChapter - " + message)
            else:
                message = "Did not remove chapter since the chapter num is empty."
                UIWidgets.showMessage(message)
                print("removeChapter - " + message)

        @classmethod
        def getChapterName(cls, chapterNum):
            propertyName = cls.getChapterNamePropertyID(chapterNum)
            return readJSONProperty(Chapters.getCurrBookChapterInfoJSONPath(), propertyName)

        @classmethod
        def getChapterLatestSubchapter(cls, chapterNum):
            propertyName = cls.getChapterLatestSubchapterPropertyID(chapterNum)
            return readJSONProperty(Chapters.getCurrBookChapterInfoJSONPath(), propertyName)

        @classmethod
        def getChapterName(cls, chapterNum):
            propertyName = cls.getChapterNamePropertyID(chapterNum)
            return readJSONProperty(Chapters.getCurrBookChapterInfoJSONPath(), propertyName)

        @classmethod
        def getCurrChapterImIndex(cls):
            chapterNum = Settings.readProperty(Settings.currChapter_ID)[2:]
            propertyName = cls.getChapterImIndexPropertyID(chapterNum)
            return readJSONProperty(Chapters.getCurrBookChapterInfoJSONPath(), propertyName)
        
        @classmethod
        def getChapterStartPage(cls, chapterNum):
            propertyName = cls.ch_ID + chapterNum + cls.ch_startPage_ID
            return readJSONProperty(Chapters.getCurrBookChapterInfoJSONPath(), propertyName)
        
        @classmethod
        def updateChapterName(cls, chapterNum, chName):
            propertyName = cls.getChapterNamePropertyID(chapterNum)
            updateJSONProperty(Chapters.getCurrBookChapterInfoJSONPath(), propertyName, chName)
            
            message = "Updated " + propertyName + " to: " + chName
            UIWidgets.showMessage(message)
            print("updateChapterName - " + message)
        
        @classmethod
        def updateChapterLatestSubchapter(cls, chapterNum, latestSubchapter):
            propertyName = cls.getChapterLatestSubchapterPropertyID(chapterNum)
            updateJSONProperty(Chapters.getCurrBookChapterInfoJSONPath(), propertyName, latestSubchapter)
            
            message = "Updated " + propertyName + " to: " + latestSubchapter
            # UIWidgets.showMessage(message)
            print("updateChapterName - " + message)
        
        @classmethod
        def updateChapterStartPage(cls, chapterNum, chStartPage):
            propertyName = cls.ch_ID + chapterNum + cls.ch_startPage_ID
            updateJSONProperty(Chapters.getCurrBookChapterInfoJSONPath(), propertyName, chStartPage)  

            message = "Updated " + propertyName + " to: " + chStartPage
            UIWidgets.showMessage(message)
            print("updateChapterStartPage - " + message)
        
        @classmethod
        def updateChapterImageIndex(cls, chapterNum, chimIndex):
            propertyName = cls.ch_ID + chapterNum + cls.ch_imageIndex_ID
            updateJSONProperty(Chapters.getCurrBookChapterInfoJSONPath(), propertyName, chimIndex)  

            message = "Updated " + propertyName + " to: " + chimIndex
            # UIWidgets.showMessage(message)
            print("updateChapterImageIndex - " + message)

    class SubchaptersProperties:
        subch_ID = "subch_"
        subch_name_ID = "_name"
        subch_startPage_ID = "_startPage"

        @classmethod
        def _getEmptySubchapter(cls, subchNum):
            subchString = Chapters.SubchaptersProperties.subch_ID + subchNum
            outSubchDict = {}
            outSubchDict[cls.getSubchapterNamePropertyID(subchNum)] = ""
            outSubchDict[cls.getSubchapterStartPagePropertyID(subchNum)] = ""
            return subchString, outSubchDict

        @classmethod
        def addSubchapter(cls, chNum, subchNum, subchName, subchStartPage):
            chString = Chapters.ChapterProperties.ch_ID + chNum
            if chNum != None and subchNum != None:
                emptySubchName, emptySubchapter = cls._getEmptySubchapter(subchNum)
                if subchName != None:
                    emptySubchapter[cls.getSubchapterNamePropertyID(subchNum)] = subchName
                if subchStartPage != None:
                    emptySubchapter[cls.getSubchapterStartPagePropertyID(subchNum)] = subchStartPage
                
                jsonData = readJSONfile(Chapters.getCurrBookChapterInfoJSONPath())
                chString = Chapters.ChapterProperties.ch_ID + chNum
                if chString in jsonData:
                    if emptySubchName not in jsonData[chString][chString + Chapters.ChapterProperties.ch_subchapters_ID]:
                        jsonData[Chapters.ChapterProperties.ch_ID + chNum][chString + Chapters.ChapterProperties.ch_subchapters_ID][emptySubchName] = emptySubchapter
                        writeJSONfile(Chapters.getCurrBookChapterInfoJSONPath(), jsonData)
                        
                        message = "Created subchapter: " + subchNum + "\nwith Name: " + subchName + "\nwith starting page: " + subchStartPage
                        UIWidgets.showMessage(message)
                        print("addSubchapter - " + message)
                    else:
                        message = "Did not create subchapter: " + subchNum + ". It is already in the data."
                        UIWidgets.showMessage(message)
                        print("addSubchapter - " + message)
                else:
                    message = "Did not add subchchapter since the chapter does not exist."
                    UIWidgets.showMessage(message)
                    print("addSubchapter - " + message)
            else: #subch or ch are None
                if chNum == None:
                    message = "Did not add subchchapter since the chapter num is empty."
                    UIWidgets.showMessage(message)
                    print("addSubchapter - " + message)
                else:
                    # subchNum is None
                    message = "Did not add subchchapter since the subchNum num is empty."
                    UIWidgets.showMessage(message)
                    print("addSubchapter - " + message)
        
        @classmethod
        def removeSubchapter(cls, chNum, subchNum):
            chString = Chapters.ChapterProperties.ch_ID + chNum
            if chNum != None and subchNum != None:
                jsonData = readJSONfile(Chapters.getCurrBookChapterInfoJSONPath())
                if chString in jsonData:
                    if cls.subch_ID + subchNum in  jsonData[chString][Chapters.ChapterProperties.getChapterSubchaptersPropertyID(chNum)]:
                            jsonData[chString][Chapters.ChapterProperties.getChapterSubchaptersPropertyID(chNum)].pop(cls.subch_ID + subchNum)
                            writeJSONfile(Chapters.getCurrBookChapterInfoJSONPath(), jsonData)
                            message = "removed subchapter: " + subchNum
                            UIWidgets.showMessage(message)
                            print("removeChapter - " + message)
                    else:
                        message = "Did not remove subchapter: " + subchNum + ". It was not in the chapter settings data."
                        UIWidgets.showMessage(message)
                        print("removeSubchapter - " + message)
                else:
                    message = "Did not remove subchapter: " + subchNum + ". Chapter was not in the chapter settings data."
                    UIWidgets.showMessage(message)
                    print("removeSubhcapter - " + message)
            else:
                if (chNum == None):
                    message = "Did not remove chapter since the chapter num is empty."
                else: #subch is None
                    message = "Did not remove chapter since the subchapter num is empty."
                UIWidgets.showMessage(message)
                print("removeSubchapter - " + message)

        @classmethod
        def updateSubchapterName(cls, subchapterNum, subchName):
            propertyName = cls.subch_ID + subchapterNum + cls.subch_name_ID
            updateJSONProperty(Chapters.getCurrBookChapterInfoJSONPath(), propertyName, subchName)

            message = "Updated " + propertyName + " to: " + subchName
            UIWidgets.showMessage(message)
            print("updateSubchapterName - " + message)
        
        @classmethod
        def getSubchapterStartPage(cls, subchapterNum):
            propertyName = cls.subch_ID + subchapterNum + cls.subch_startPage_ID
            readJSONProperty(Chapters.getCurrBookChapterInfoJSONPath(), propertyName)
        
        @classmethod
        def updateSubchapterStartPage(cls, subchapterNum, subchStartPage):
            propertyName = cls.subch_ID + subchapterNum + cls.subch_startPage_ID
            updateJSONProperty(Chapters.getCurrBookChapterInfoJSONPath(), propertyName, subchStartPage)  

            message = "Updated " + propertyName + " to: " + subchStartPage
            UIWidgets.showMessage(message)
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
            readJSONProperty(Chapters.getCurrBookChapterInfoJSONPath(), propertyName)
    
    @classmethod 
    def getCurrBookChapterInfoJSONPath(cls):
        currBookName = Settings.readProperty(Settings.currBookName_ID)
        bookFolderPath = Settings.getBookFolderPath(currBookName)
        return cls._getBookChapterInfoJSONPath(bookFolderPath)
    
    @classmethod
    def _getBookChapterInfoJSONPath(cls, bookFolderPath):
        return bookFolderPath + cls.chaptersSettingsRelPath

    @classmethod
    def readProperty(cls, property):
        return readJSONProperty(cls.getCurrBookChapterInfoJSONPath(), property)


class TexFile:

    def _getCurrTexFilesDir(currSubchapter):
        currChapter = Settings.readProperty(Settings.currChapter_ID)
        return Settings.getBookFolderPath(Settings.readProperty(Settings.currBookName_ID)) + \
                "/" + currChapter + "/" + \
                Settings.relToSubchapters_Path + \
                "/ch_" + currSubchapter
    
    @classmethod
    def _getCurrContentFilepath(cls):
        currSubchapter = Settings.readProperty(Settings.currChapterFull_ID)
        return cls._getCurrTexFilesDir(currSubchapter) + "/" + currSubchapter + "_con.tex"
    
    @classmethod
    def _getCurrTOCFilepath(cls):
        currSubchapter = Settings.readProperty(Settings.currChapterFull_ID)
        return cls._getCurrTexFilesDir(currSubchapter) + "/" + currSubchapter + "_toc.tex"
    
    @classmethod      
    def _getCurrMainFilepath(cls):
        currSubchapter = Settings.readProperty(Settings.currChapterFull_ID)
        return cls._getCurrTexFilesDir(currSubchapter) + "/" + currSubchapter + "_main.tex"

    def _populateMainFile():
        contentFile = []
        tocFile = []

        localLinksLine = ""
        with open(TexFile._getCurrContentFilepath(), 'r') as contentF:
            # create the local links line
            contentFile = contentF.readlines()
            
            imLinkNameToken = "\def\linkname{"
            myTargetToken = "\myTarget{"
            
            listOfLocalLinks = []
            for i in range(0, len(contentFile)):
                line = contentFile[i]
                if imLinkNameToken in line:
                    imLinkName = contentFile[i].replace(imLinkNameToken, "")[:-1]
                    imLinkName = imLinkName.replace(" ", "")
                    imLinkName = imLinkName.replace("}", "")

                    imageAndScriptPath = contentFile[i + 2].replace(myTargetToken, "")[:-1]
                    imageAndScriptPath = imageAndScriptPath.split("}")[0]
                    imageAndScriptPath = imageAndScriptPath.replace(" ", "")
                    
                    localLinksLine = "        \\href{file:" + imageAndScriptPath + ".sh" + "}{" + imLinkName + "},\n"
                    listOfLocalLinks.append(localLinksLine)
                    # i += 2

            localLinksLine = "      [" + "\n" + "".join(listOfLocalLinks) + "        ]"
        
        with open(TexFile._getCurrTOCFilepath(), 'r') as tocF:
            tocFile = tocF.readlines()
                
        with open(os.getenv("BOOKS_PROCESS_TEX_PATH") + "/template.tex", 'r') as templateF:
            templateFile = templateF.readlines()
            templateFile= [i.replace("[_PLACEHOLDER_CHAPTER_]", Settings.readProperty(Settings.currChapter_ID)) for i in templateFile]

        with open(TexFile._getCurrMainFilepath(), 'w') as outFile:

            outFileList = []
            # get the marker of the part BEFORE_LOCAL_LINKS_MARKER
            # 
            # replace everything before marker from template 
            beforeLocalLinksMarker = "BEFORE_LOCAL_LINKS_MARKER"
            beforeLocalLinksmarkerPosTemplate = next(i for i,v in enumerate(templateFile) if beforeLocalLinksMarker in v)
            outFileList = templateFile[:beforeLocalLinksmarkerPosTemplate + 1]

            # add local links
            outFileList.append("  " + localLinksLine + "\n")
            
            # add TOC from template
            beforeTOCmarker = "BEFORE_TOC_MARKER"
            beforeTOCmarkerPosTemplate = next(i for i,v in enumerate(templateFile) if beforeTOCmarker in v)
            outFileList.extend(templateFile[beforeLocalLinksmarkerPosTemplate + 1:beforeTOCmarkerPosTemplate + 1])          

            # add TOC data
            outFileList.extend(["        " + i for i in tocFile])
            
            # get the marker of the part AFTER TOC and BEFORE IMAGES
            # 
            # replace everything betweeen markers
            afterTOCmarker = "AFTER_TOC_MARKER"
            # afterTOCmarkerPos = next(i for i,v in enumerate(texFile) if afterTOCmarker in v)
            afterTOCmarkerPosTem = next(i for i,v in enumerate(templateFile) if afterTOCmarker in v)
            beforePICmarker = "BEFORE_PIC_MARKER"
            beforePICmarkerPosTem = next(i for i,v in enumerate(templateFile) if beforePICmarker in v)
            outFileList.extend(templateFile[afterTOCmarkerPosTem: beforePICmarkerPosTem + 1])

            # add CONTENT
            outFileList.extend(contentFile)

            # add extra 2 lines
            outFileList.extend("\n\n")

            # get the marker of the part in the END
            # 
            # replace everything after marker from template 
            afterPICmarker = "AFTER_PIC_MARKER"
            afterPICmarkerPosTem = next(i for i,v in enumerate(templateFile) if afterPICmarker in v)
            outFileList.extend(templateFile[afterPICmarkerPosTem:])
            
            # writeToMainFile
            for line in outFileList:
                outFile.write(line)

    @classmethod 
    def buildCurrentSubchapterPdf(cls):
        currSubchapter = Settings.readProperty(Settings.currChapterFull_ID)
        currTexFilesFolder = cls._getCurrTexFilesDir(currSubchapter)
        currTexMainFile = cls._getCurrContentFilepath()
        print("ChapterLayout.set - " + currTexMainFile)
        _waitDummy = os.system("${BOOKS_ON_FILE_SAVE_PATH}/s_onTexFileSave.sh " + currTexMainFile + " " + currTexFilesFolder)
        UIWidgets.tkVariables.needRebuild.set(False)

