import sys
import os
from time import sleep
import tkinter as tk
from threading import Thread

import _utils._utils_main as _u
import UI.widgets_manager as uim
import layouts.layouts_utils as _layouts_utils
import tex_file.create_tex_file as t
import file_system.file_system_main as fs


'''
Note: layout classes names are used to compare with json and and m_main to add UI
        so change with caution
'''


class Layout:
    @classmethod
    def clsInit(cls):
        raise NotImplementedError()


    @classmethod
    def set(cls, mainWinRoot):
        raise NotImplementedError()

 
    def setUIElements(winMainRoot):
        raise NotImplementedError()


class ChapterLayout(Layout):
    layoutUInames = []
    pyAppDimensions = [None, None]
    

    @classmethod
    def set(cls, mainWinRoot):
        '''
        # chapter: 
        #       skim chapter to the right 
        #       vscode to the left
        '''
        # set menu dimensions
        mainWinRoot.geometry(str(cls.pyAppDimensions[0]) + "x" + str(cls.pyAppDimensions[1]))
       
        # Open chapter pdf in skim
        mon_width, mon_height = _u.getMonitorSize()
        mon_halfWidth = mon_width / 2
        currChapter = fs.BookInfoStructure.readProperty(fs.BookInfoStructure.currSection_ID)
        currChapterFull = fs.BookInfoStructure.readProperty(fs.BookInfoStructure.currSectionFull_ID)
        ownerName, windowID = _u.getOwnersName_windowID_ofApp("skim", currChapterFull)
        
        if ownerName == None or windowID == None:
            t.TexFile.buildCurrentSubchapterPdf()

            # if the pdf was not opened in Skim already   
            pathToChapterFolder = _u.getPathToBooks() +  _u.Settings.readProperty(_u.Settings.getCurrentBookFolderName()) + "/" + currChapter + "/subchapters/ch_" + currChapterFull + "/" + currChapterFull + "_main.pdf"
            _waitDummy = _layouts_utils.openPdfInSkim(pathToChapterFolder)
            # sleep(0.5)
            ownerName, windowID = _u.getOwnersName_windowID_ofApp(_u.Settings.skim_ID, currChapterFull)
        

        _layouts_utils.moveApplicationsWindow(ownerName, windowID, [mon_halfWidth, mon_height - cls.pyAppDimensions[1] - 100, cls.pyAppDimensions[0], cls.pyAppDimensions[1] + 54])
    
        # open chapter source in vscode
        pathToSourceFolder = _u.getPathToBooks() +  _u.Settings.readProperty(_u.Settings.getCurrentBookFolderName()) + "/" + currChapter + "/subchapters/ch_" + currChapterFull #+ ".tex"
        ownerName, windowID = _u.getOwnersName_windowID_ofApp("vscode", currChapterFull)
        
        if (windowID == None):
            _waitDummy = os.system("code -n " + pathToSourceFolder)
            ownerName = None
            windowID = None
            while windowID == None:
                ownerName, windowID = _u.getOwnersName_windowID_ofApp("vscode", currChapterFull)
                sleep(0.1)
        
        #move vscode into position
        _layouts_utils.moveApplicationsWindow(ownerName, windowID, [mon_halfWidth, (mon_height) * 2 , 0 , 0])
        _layouts_utils.moveApplicationsWindow(ownerName, windowID, [mon_halfWidth, (mon_height) * 2 , 0 , 0])

        if ui.UItkVariables.needRebuild.get() == True:
            Thread(target = t.TexFile.buildCurrentSubchapterPdf).start()


    # @classmethod
    # def setUIElements(cls, winMainRoot):
    #     ui.UItkVariables.needRebuild = tk.BooleanVar()

    #     layoutOM = ui.UIWidgets.getOptionsMenu_Layouts(winMainRoot, cls.__name__)
    #     layoutOM.grid(column=0, row=0, padx=0, pady=0)
    #     layoutOM.update()
        
    #     showProofsBTN = ui.UIWidgets.getShowProofs_BTN(winMainRoot, cls.__name__)
    #     showProofsBTN.grid(column=1, row=0, padx=0, pady=0)

    #     dummyEntry = tk.Entry(winMainRoot, text = "Dummy", name = cls.__name__.lower() + "_dummyFocusEntry")
    #     dummyEntry.grid(column=2, row=0, padx=0, pady=0)
    #     dummyEntry.focus_set()

    #     saveImageBTN = ui.UIWidgets.getSaveImage_BTN(winMainRoot, cls.__name__)
    #     saveImageBTN.grid(column=3, row=0, padx=0, pady=0)

    #     createGlLinkBTN, createGlLinkETR = ui.UIWidgets.getGlobalLinksAdd_Widgets(winMainRoot, cls.__name__)
    #     createGlLinkETR.grid(column=4, row=0, padx=0, pady=0)
    #     createGlLinkBTN.grid(column=5, row=0, padx=0, pady=0)


    #     mon_width, _ = _u.getMonitorSize()
    #     cls.pyAppDimensions[0] = int(mon_width / 2)
    #     cls.pyAppDimensions[1] = layoutOM.winfo_height() + 5


class MainLayout(Layout):
    layoutUInames = []
    pyAppDimensions = [None, None]
    
    @classmethod
    def set(cls, mainWinRoot):
        '''
        # main:
        #       full book to the left
        #       vscode/finder(with images folder) to the right
        '''
        ui.UItkVariables.needRebuild.set(False)

        #close the chapter vscode if it open
        _, windowID = _u.getOwnersName_windowID_ofApp("vscode", _u.Settings.readProperty(_u.BookSettings.CurrentStateProperties.Book.currSectionFull_ID))
        
        if (windowID != None):
            osascript = "osascript -e '\
    tell application \"System Events\" to tell process \""  + _u.Settings.vsCode_ID + "\"\n\
	    tell window " + windowID + "\n\
            click button 1\n\
	    end tell\n\
    end tell'"
            os.system(osascript)

        # change the manu size
        mainWinRoot.geometry(str(cls.pyAppDimensions[0]) + "x" + str(cls.pyAppDimensions[1]))

        # whole book in skim
        mon_width, mon_height = _u.getMonitorSize()
        mon_halfWidth = mon_width / 2

        openWholeBook([mon_halfWidth, mon_height * 2],[0, 0])

        # currChapter images folder
        currChapter = fs.BookInfoStructure.readProperty(fs.BookInfoStructure.currSection_ID)
        ownerName, windowID = _u.getOwnersName_windowID_ofApp("finder", currChapter + "_images")
        
        if ownerName == None or windowID == None:
            # if no window found we open one with the chapter in Finder
            pathToChapterFolder = _u.getPathToBooks() +  _u.Settings.readProperty(_u.Settings.getCurrentBookFolderName()) + \
                                    "/" + currChapter + "/" + currChapter + "_images"
            _waitDummy = _layouts_utils.openChapterFolderInFinder(pathToChapterFolder)
            ownerName, windowID = _u.getOwnersName_windowID_ofApp("finder",currChapter + "_images")
        
        if ownerName == None or windowID == None: 
            print("setMainLayout - Something went wrong. Finder could not open the folder")
        else:
            _layouts_utils.moveApplicationsWindow(ownerName, 
                                            windowID, 
                                            [mon_halfWidth, mon_height - cls.pyAppDimensions[1], cls.pyAppDimensions[0], cls.pyAppDimensions[1] + 54])

        _u.Settings.currLayout = cls.__name__.replace(_u.Settings.layoutClass_ID, "")


    # @classmethod
    # def setUIElements(cls, winMainRoot):
    #     mon_width, _ = _u.getMonitorSize()
    #     cls.pyAppDimensions = [int(mon_width / 2), 90]

    #     chooseBookOM = ui.UIWidgets.ChooseBookChapter.getOptionsMenu_ChooseBook(winMainRoot, cls.__name__)
    #     chooseBookOM.grid(column = 0, row = 0, padx = 0, pady = 0)

    #     layoutOM = ui.UIWidgets.getOptionsMenu_Layouts(winMainRoot, cls.__name__)
    #     layoutOM.grid(column = 0, row = 1, padx = 0, pady = 0)

    #     imageGenerationUI = ui.UIWidgets.getTextEntryButton_imageGeneration(winMainRoot, cls.__name__)
    #     imageGenerationUI[0].grid(column = 1, row = 0, padx = 0, pady = 0, sticky = tk.N)
    #     imageGenerationUI[1].grid(column = 1, row = 1, padx = 0, pady = 0, sticky = tk.N)

    #     addExtraImage = ui.UIWidgets.getAddImage_BTN(winMainRoot, cls.__name__)
    #     addExtraImage.grid(column = 1, row = 0, padx = 0, pady = 0, sticky = tk.E)

    #     imageGenerationRestartBTN = ui.UIWidgets.getImageGenerationRestart_BTN(winMainRoot, cls.__name__)
    #     imageGenerationRestartBTN.grid(column = 1, row = 0, padx = 0, pady = 0, sticky = tk.W)

    #     TOCcreate_CB, TOCWithImage_CB = ui.UIWidgets.getCheckboxes_TOC(winMainRoot, cls.__name__)
    #     TOCcreate_CB.grid(column = 1, row = 1, padx = 0, pady = 0, sticky = tk.W)
    #     TOCWithImage_CB.grid(column = 1, row = 1, padx = 0, pady = 0, sticky = tk.E)
        
    #     currScrShotDirText = ui.UIWidgets.Screenshot.getText_CurrentScreenshotDir(winMainRoot, cls.__name__)
    #     currScrShotDirText.grid(columnspan = 2,row = 2)

    #     chooseChapterOptionMenu = ui.UIWidgets.ChooseBookChapter.getOptionMenu_ChooseChapter(winMainRoot, cls.__name__)
    #     chooseChapterOptionMenu.grid(column = 2, row = 0, padx = 0, pady = 0)

    #     chooseChapterMenusAndbackBtn = ui.ChaptersUI.getButton_chooseChaptersMenusAndBack(winMainRoot, cls.__name__)
    #     chooseChapterMenusAndbackBtn.grid(column = 3, row = 0, padx = 0, pady = 0)

    #     chooseSubChapterMenu = ui.UIWidgets.ChooseBookChapter.getOptionMenu_ChooseSubchapter(winMainRoot, cls.__name__)
    #     chooseSubChapterMenu.grid(column = 3, row = 2, padx = 0, pady = 0)


class WholeVSCodeLayout(Layout):
    layoutUInames = []
    pyAppDimensions = [None, None]
   
    @classmethod
    def set(cls, mainWinRoot):
        mainWinRoot.geometry(str(cls.pyAppDimensions[0]) + "x" + str(cls.pyAppDimensions[1]))

        mon_windth, mon_height = _u.getMonitorSize()
        # vscode open
        ownerName, windowID = _u.getOwnersName_windowID_ofApp("vscode")
        _layouts_utils.moveApplicationsWindow(ownerName, windowID, [mon_windth, mon_height , 0 , 0])

   
    @classmethod
    def setUIElements(cls, winMainRoot):
        layoutOM = ui.UIWidgets.getOptionsMenu_Layouts(winMainRoot, cls.__name__)
        layoutOM.grid(column=0, row=0, padx=0, pady=0)
        layoutOM.update()
        cls.pyAppDimensions[0] = layoutOM.winfo_width()
        cls.pyAppDimensions[1] = layoutOM.winfo_height()


