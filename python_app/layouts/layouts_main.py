import sys
import os
from time import sleep
import tkinter as tk
from threading import Thread

import _utils._utils_main as _u
import UI.widgets_vars as wv
import layouts.layouts_utils as lu
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


class SectionLayout(Layout):
    layoutUInames = []
    pyAppDimensions = [None, None]    

    @classmethod
    def set(cls, mainWinRoot, menuWidth, menuHeight):
        '''
        # Section: 
        #       skim Section to the right 
        #       vscode to the left
        '''
        # Open chapter pdf in skim
        mon_width, mon_height = _u.getMonitorSize()
        mon_halfWidth = mon_width / 2
        
        # set menu dimensions
        mainWinRoot.geometry(str(menuWidth) + "x" + str(menuHeight) + "+" + str(int(mon_halfWidth)) + "+0")
       
        currSection = fs.BookInfoStructure.readProperty(fs.BookInfoStructure.PubProp.currSection_ID)
        secPrefix = fs.BookInfoStructure.readProperty(fs.BookInfoStructure.PubProp.sections_prefix_ID)
        ownerName, windowID = _u.getOwnersName_windowID_ofApp("skim", currSection)
        
        if ownerName == None or windowID == None:
            t.TexFile.buildCurrentSubsectionPdf()

            # if the pdf was not opened in Skim already   
            pathToChapterFolder = _u.getCurrentSectionAbsDir() + "/" + secPrefix + "_" + currSection + "_main.pdf"
            _waitDummy = lu.openPdfInSkim(pathToChapterFolder)
            # sleep(0.5)
            ownerName, windowID = _u.getOwnersName_windowID_ofApp(_u.Settings._appsIDs.skim_ID, currSection)
        

        lu.moveApplicationsWindow(ownerName, 
                                windowID, 
                                [mon_halfWidth, mon_height - menuHeight - 100, menuWidth, menuHeight + 54])
    
        # open chapter source in vscode
        pathToSourceFolder = _u.getCurrentSectionAbsDir()
        ownerName, windowID = _u.getOwnersName_windowID_ofApp("vscode", currSection)
        
        if (windowID == None):
            _waitDummy = os.system("code -n " + pathToSourceFolder)
            ownerName = None
            windowID = None
            while windowID == None:
                ownerName, windowID = _u.getOwnersName_windowID_ofApp("vscode", currSection)
                sleep(0.1)
        
        #move vscode into position
        lu.moveApplicationsWindow(ownerName, windowID, [mon_halfWidth, (mon_height) * 2 , 0 , 0])
        lu.moveApplicationsWindow(ownerName, windowID, [mon_halfWidth, (mon_height) * 2 , 0 , 0])

        if wv.UItkVariables.needRebuild.get() == True:
            Thread(target = t.TexFile.buildCurrentSubsectionPdf).start()


class MainLayout(Layout):
    layoutUInames = []
    pyAppDimensions = [None, None]
    
    @classmethod
    def set(cls, mainWinRoot, appWidth, appHeight):
        '''
        # main:
        #       full book to the left
        #       vscode/finder(with images folder) to the right
        '''
        wv.UItkVariables.needRebuild.set(False)

        #close the chapter vscode if it open
        _, windowID = _u.getOwnersName_windowID_ofApp(
                            "vscode",
                             fs.BookInfoStructure.readProperty(fs.BookInfoStructure.PubProp.currSection_ID))
        
        if (windowID != None):
            osascript = "osascript -e '\
    tell application \"System Events\" to tell process \""  + _u.Settings.vsCode_ID + "\"\n\
	    tell window " + windowID + "\n\
            click button 1\n\
	    end tell\n\
    end tell'"
            os.system(osascript)


        # whole book in skim
        mon_width, mon_height = _u.getMonitorSize()
        mon_halfWidth = mon_width / 2
        
        # change the manu size
        mainWinRoot.geometry(str(appWidth) + "x" + str(appHeight) + "+" + str(int(mon_halfWidth)) + "+0")

        lu.openWholeBook([mon_halfWidth, mon_height * 2],[0, 0])

        # currChapter images folder
        currSection = fs.BookInfoStructure.readProperty(fs.BookInfoStructure.PubProp.currSection_ID)
        ownerName, windowID = _u.getOwnersName_windowID_ofApp("finder", currSection + "_images")
        
        if ownerName == None or windowID == None:
            # if no window found we open one with the chapter in Finder
            currScreenshotDir = _u.getCurrentScreenshotAbsDir()
            _waitDummy = lu.openChapterFolderInFinder(currScreenshotDir)
            # TODO: this needs to change
            ownerName, windowID = _u.getOwnersName_windowID_ofApp("finder", "images")
        
        if ownerName == None or windowID == None: 
            print("setMainLayout - Something went wrong. Finder could not open the folder")
        else:
            lu.moveApplicationsWindow(ownerName, 
                                            windowID, 
                                            [mon_halfWidth, mon_height - appHeight, appWidth, appHeight + 54])

        _u.Settings.currLayout = cls.__name__.replace(_u.Settings.layoutClassToken, "")


class WholeVSCodeLayout(Layout):
    layoutUInames = []
    pyAppDimensions = [None, None]
   
    @classmethod
    def set(cls, mainWinRoot):
        mainWinRoot.geometry(str(cls.pyAppDimensions[0]) + "x" + str(cls.pyAppDimensions[1]))

        mon_windth, mon_height = _u.getMonitorSize()
        # vscode open
        ownerName, windowID = _u.getOwnersName_windowID_ofApp("vscode")
        lu.moveApplicationsWindow(ownerName, windowID, [mon_windth, mon_height , 0 , 0])




