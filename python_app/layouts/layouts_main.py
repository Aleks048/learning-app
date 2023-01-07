import os, subprocess, signal, psutil
from time import sleep
from threading import Thread

import layouts.layouts_utils as lu

import _utils._utils_main as _u
import _utils.logging as log
import UI.widgets_manager as wm
import tex_file.tex_file_manager as tm
import file_system.file_system_manager as fsm
import data.temp as dt


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
    def set(cls, mainWinRoot = None, menuWidth = 0, menuHeight = 0):
        '''
        # Section: 
        #       skim Section to the right 
        #       vscode to the left
        '''

        pathToSourceFolder = fsm.Wr.Paths.Section.getAbs_curr()
        currSection = fsm.Wr.SectionCurrent.readCurrSection()
        secPrefix = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.sections_prefix_ID)
        
        # check if the folder is empty.      
        if len(os.listdir(os.path.join(pathToSourceFolder, secPrefix + "_" + currSection + "_images"))) == 0:
            msg = "No images yet. Can't switch to section."
            wm.Wr.MessageMenu.createMenu(msg)
            log.autolog(msg)
            return
        else:
            # rebuild the section doc
            # NOTE: do we need a rebuild each time we switch??
            wm.Data.UItkVariables.needRebuild.set(True)
        
        if wm.Data.UItkVariables.needRebuild.get() == True:
            _waitDummy = tm.Wr.TexFile.buildCurrentSubsectionPdf()

        # Open section pdf in skim
        mon_width, mon_height = _u.getMonitorSize()
        mon_halfWidth = mon_width / 2
        
        # set menu dimensions
        if mainWinRoot != None:
            mainWinRoot.geometry(str(menuWidth) + "x" + str(menuHeight) 
                                + "+" + str(int(mon_halfWidth)) + "+0")
        
        ownerName, windowID, ownerPID = _u.getOwnersName_windowID_ofApp("skim", currSection)
        
        if ownerName == None or windowID == None:
            # if the pdf was not opened in Skim already   
            pathToSectionFolder = os.path.join(fsm.Wr.Paths.Section.getAbs_curr(), 
                                                secPrefix + "_" + currSection + "_main.myPDF")
            _waitDummy = lu.openPdfInSkim(pathToSectionFolder)
            # sleep(0.5)
            ownerName, windowID, ownerPID = \
                _u.getOwnersName_windowID_ofApp(_u.Settings._appsIDs.skim_ID, currSection)
        

        lu.moveApplicationsWindow(ownerName, 
                                windowID,
                                ownerPID,
                                [mon_halfWidth, mon_height - menuHeight - 24, menuWidth, menuHeight + 54])
        lu.moveApplicationsWindow(ownerName, 
                                windowID, 
                                ownerPID,
                                [mon_halfWidth, mon_height - menuHeight - 24, menuWidth, menuHeight + 54])
    
        # open chapter source in vscode
        # ownerName, windowID, ownerPID = _u.getOwnersName_windowID_ofApp("vscode", currSection)
        
        # if (windowID == None):
        cmd = "exec code -n "+ pathToSourceFolder + " &"
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)

        # ownerName = None
        windowID = None
        while windowID == None:
            ownerName, windowID, ownerPID = _u.getOwnersName_windowID_ofApp("vscode", currSection)
            dt.OtherAppsInfo.VsCode.section_pid  = ownerPID

        vscodeBounds = [mon_halfWidth, mon_height , 0 , 0]
        vscodeBounds  = [str(i) for i in vscodeBounds]
        vscodeWindowCmd = "\
                        set size to {" + vscodeBounds[0] + ", " + vscodeBounds[1] + "}\n\
                        delay 0.1\n\
                        set position to {" + vscodeBounds[2] + ", " + vscodeBounds[3] + "}\n\
                        delay 0.1\n\
                        perform action \"AXRaise\"\n"
        # move vscode into position
        lu.moveApplicationsWindow(ownerName,
                                windowID,
                                ownerPID,
                                vscodeBounds,
                                currSection,
                                vscodeWindowCmd)

        # create the layout in the vscode window
        conterntFilepath = fsm.Wr.Paths.TexFiles.Content.getAbs_curr()
        TOCFilepath = fsm.Wr.Paths.TexFiles.TOC.getAbs_curr()
        cmd = "osascript -e '\n\
        set theprocs to every process whose unix id is " + ownerPID + "\n\
        set proc to item 1 of theprocs\n\
        tell proc to activate\n\
        '"
        _waitDummy = os.system(cmd)
        
        cmd = "osascript -e '\n\
        tell application \"System Events\"\n\
            keystroke \"kw\" using {command down}\n\
            keystroke \"b\" using {command down, option down}\n\
        end tell\n\
        '"
        _waitDummy = os.system(cmd)

        _waitDummy = os.system("code " + TOCFilepath + " " + conterntFilepath)


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
        wm.Data.UItkVariables.needRebuild.set(False)
        currSection = fsm.Wr.SectionCurrent.readCurrSection()

        #close the chapter vscode if it open
        log.autolog("hip: " + dt.OtherAppsInfo.VsCode.section_pid)
        if dt.OtherAppsInfo.VsCode.section_pid != _u.Token.NotDef.str_t:
            mon_width, mon_height = _u.getMonitorSize()
            mon_halfWidth = mon_width / 2
            vscodeBounds = [mon_halfWidth, mon_height , 0 , 0]
            vscodeWindowCmd = "\
                        click button 1\n"
            ownerName, windowID, ownerPID = _u.getOwnersName_windowID_ofApp("vscode", currSection)
            # move vscode into position
            lu.moveApplicationsWindow(ownerName,
                                    windowID,
                                    str(ownerPID),
                                    vscodeBounds,
                                    currSection,
                                    vscodeWindowCmd)

        # whole book in skim
        mon_width, mon_height = _u.getMonitorSize()
        mon_halfWidth = mon_width / 2
        
        # change the manu size
        mainWinRoot.geometry(str(appWidth) + "x" + str(appHeight) 
                        + "+" + str(int(mon_halfWidth)) + "+0")

        lu.openWholeBook([mon_halfWidth, mon_height * 2],[0, 0])

        # currChapter images folder
        currSectionWPrefix = fsm.Wr.SectionCurrent.getSectionNameWprefix()
        ownerName, windowID, ownerPID = _u.getOwnersName_windowID_ofApp("finder", currSectionWPrefix + "_images")
        
        if ownerName == None or windowID == None:
            # if no window found we open one with the chapter in Finder
            currScreenshotDir = fsm.Wr.Paths.Screenshot.getAbs_curr()
            _waitDummy = lu.openChapterFolderInFinder(currScreenshotDir)
            # TODO: this needs to change
            ownerName, windowID, ownerPID = _u.getOwnersName_windowID_ofApp("finder", "images")
        
        if ownerName == None or windowID == None: 
            print("setMainLayout - Something went wrong. Finder could not open the folder")
        else:
            lu.moveApplicationsWindow(ownerName, 
                                    windowID,
                                    ownerPID,
                                    [mon_halfWidth, mon_height - appHeight - 105, appWidth, appHeight + 54])
            lu.moveApplicationsWindow(ownerName, 
                                    windowID,
                                    ownerPID,
                                    [mon_halfWidth, mon_height - appHeight - 105, appWidth, appHeight + 54])

        _u.Settings.currLayout = cls.__name__.replace(_u.Settings.layoutClassToken, "")


class WholeVSCodeLayout(Layout):
    layoutUInames = []
    pyAppDimensions = [None, None]
   
    @classmethod
    def set(cls, mainWinRoot):
        mainWinRoot.geometry(str(cls.pyAppDimensions[0]) + "x" + str(cls.pyAppDimensions[1]))

        mon_windth, mon_height = _u.getMonitorSize()
        # vscode open
        ownerName, windowID, ownerPID = _u.getOwnersName_windowID_ofApp("vscode")
        lu.moveApplicationsWindow(ownerName, 
                                windowID, 
                                ownerPID, 
                                [mon_windth, mon_height , 0 , 0])
        lu.moveApplicationsWindow(ownerName, 
                                windowID, 
                                ownerPID,
                                [mon_windth, mon_height , 0 , 0])




