import os, subprocess
from time import sleep
from threading import Thread

import layouts.layouts_utils as lu

import _utils._utils_main as _u
import _utils.logging as log
import UI.widgets_manager as wm
import tex_file.tex_file_manager as tm
import file_system.file_system_manager as fsm
import data.temp as dt
import scripts.osascripts as oscr


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
        
        if dt.OtherAppsInfo.Finder.main_pid != _u.Token.NotDef.str_t:
            cmd = oscr.closeFinderWindow(dt.OtherAppsInfo.Finder.main_pid, currSection)
            subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).wait()
        
        if dt.OtherAppsInfo.Skim.main_pid != _u.Token.NotDef.str_t:
            _, windowName, ownerPID = _u.getOwnersName_windowID_ofApp(_u.Settings._appsIDs.skim_ID, 
                                                        _u.Settings.PubProp.wholeBook_ID + ".pdf")
            if windowName != None:
                dt.OtherAppsInfo.Skim.main_winName = windowName
                page = windowName.split("page ")
                log.autolog(page)
                if len(page) != 2:
                    log.autolog("setSectionLayout - Something went wrong. Can't get page number out of the name.")
                    return
                else:
                    page = page[-1]
                
                if type(page) == str:
                    page = page.split(" ")[0]
                    fsm.Wr.BookInfoStructure.updateProperty(fsm.PropIDs.Book.currentPage_ID, page)
                    
                    cmd = oscr.closeSkimDocument(dt.OtherAppsInfo.Skim.main_pid, _u.Settings.PubProp.wholeBook_ID)
                    log.autolog(cmd)
                    subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).wait()
        
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

 
        # set menu dimensions
        mon_width, mon_height = _u.getMonitorSize()
        mon_halfWidth = mon_width / 2
        
        if mainWinRoot != None:
            mainWinRoot.geometry(str(menuWidth) + "x" + str(menuHeight) 
                                + "+" + str(int(mon_halfWidth)) + "+0")
 
        #
        # SKIM
        #
        _, _, ownerPID = _u.getOwnersName_windowID_ofApp("skim", currSection)
        dt.OtherAppsInfo.Skim.section_pid = ownerPID

        pathToCurrSecPDF = fsm.Wr.Paths.PDF.getAbs_curr()
        
        if ownerPID == None:
            cmd = " open skim://" + pathToCurrSecPDF
            subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).wait()

        while ownerPID == None:
            _, _, ownerPID = _u.getOwnersName_windowID_ofApp(_u.Settings._appsIDs.skim_ID, currSection)
            sleep(0.1)

        dt.OtherAppsInfo.Skim.section_pid = ownerPID
        
        skimBounds = [mon_halfWidth, mon_height - menuHeight - 80, menuWidth, 0 + menuHeight + 54]
        skimBounds  = [str(i) for i in skimBounds]
        cmd = oscr.getMoveWindowCMD(ownerPID,
                                skimBounds,
                                currSection)
        subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).wait()
        log.autolog("moved SKIM")


        #
        # VSCODE
        #
        cmd = "code -n "+ pathToSourceFolder
        _ = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)

        ownerPID = None
        while ownerPID == None:
            _, _, ownerPID = _u.getOwnersName_windowID_ofApp(_u.Settings._appsIDs.vsCode_ID, currSection)
            sleep(0.1)
        
        dt.OtherAppsInfo.VsCode.section_pid  = ownerPID

        vscodeBounds = [mon_halfWidth, mon_height , 0, 0]
        vscodeBounds  = [str(i) for i in vscodeBounds]
        # move vscode into position
        cmd = oscr.getMoveWindowCMD(ownerPID,
                                vscodeBounds,
                                currSection)
        subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).wait()

        # create the layout in the vscode window
        conterntFilepath = fsm.Wr.Paths.TexFiles.Content.getAbs_curr()
        TOCFilepath = fsm.Wr.Paths.TexFiles.TOC.getAbs_curr()
        
        cmd = oscr.get_SetSecVSCode_CMD()
        subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).wait()

        cmd = "code " + TOCFilepath + " " + conterntFilepath
        subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).wait()
        log.autolog("moved VSCODE.")

        _u.Settings.currLayout = cls.__name__.replace(_u.Settings.layoutClassToken, "")
        log.autolog("DONE setting section layout.")


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

        #close the chapter VSCode if it is open
        if dt.OtherAppsInfo.VsCode.section_pid != _u.Token.NotDef.str_t:
            cmd = oscr.closeVscodeWindow(dt.OtherAppsInfo.VsCode.section_pid, currSection)
            subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).wait()
        #close the chapter Skim if it is open
        if dt.OtherAppsInfo.Skim.section_pid != _u.Token.NotDef.str_t:
            cmd = oscr.closeSkimDocument(dt.OtherAppsInfo.Skim.section_pid, currSection)
            subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).wait()

        mon_width, mon_height = _u.getMonitorSize()
        mon_halfWidth = mon_width / 2

        # change the manu size
        mainWinRoot.geometry(str(appWidth) + "x" + str(appHeight) 
                            + "+" + str(int(mon_halfWidth)) + "+0")

       
        #
        # SKIM
        #
        dimensions = [mon_halfWidth, mon_height, 0, 0]
    
        currPage = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.currentPage_ID)

        bookPath = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.originalMaterialPath_ID)
        if currPage == None or bookPath == None:
            return
        cmd = " open skim://"+ bookPath + "#page=" + currPage
        _ = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).pid
        
        _, _, ownerPID = _u.getOwnersName_windowID_ofApp(_u.Settings._appsIDs.skim_ID, 
                                                        _u.Settings.PubProp.wholeBook_ID + ".pdf")
        while ownerPID == None:
            _, _, ownerPID = _u.getOwnersName_windowID_ofApp(_u.Settings._appsIDs.skim_ID, 
                                                            _u.Settings.PubProp.wholeBook_ID + ".pdf")
            sleep(0.1)

        if ownerPID == None: 
            log.autolog("Something went wrong. Skim could not open the document")
        else:
            cmd = oscr.getMoveWindowCMD(ownerPID, 
                                        dimensions,
                                        _u.Settings.PubProp.wholeBook_ID)
            subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).wait()

        dt.OtherAppsInfo.Skim.main_pid = ownerPID


        #
        # FINDER
        #
        bounds = [mon_halfWidth, mon_height - appHeight - 80, appWidth, appHeight + 54]

        currSectionWPrefix = fsm.Wr.SectionCurrent.getSectionNameWprefix()
        _, _, ownerPID = _u.getOwnersName_windowID_ofApp("finder", currSectionWPrefix + "_images")
        dt.OtherAppsInfo.Finder.main_pid = ownerPID
        
        if ownerPID == None:
            # if no window found we open one with the chapter in Finder
            currScreenshotDir = fsm.Wr.Paths.Screenshot.getAbs_curr()
            cmd = "open file://" + currScreenshotDir
            subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).wait()
        
        while ownerPID == None:
            _, _, ownerPID = _u.getOwnersName_windowID_ofApp("finder", "images")
            sleep(0.1)
        
        dt.OtherAppsInfo.Finder.main_pid = ownerPID
        
        if ownerPID == None: 
            print("setMainLayout - Something went wrong. Finder could not open the folder")
        else:
            cmd = oscr.getMoveWindowCMD(ownerPID,
                                    bounds,
                                    currSection)
            subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).wait()
        
        log.autolog("Moved Finder.")

        _u.Settings.currLayout = cls.__name__.replace(_u.Settings.layoutClassToken, "")
        log.autolog("DONE setting section layout.")


class WholeVSCodeLayout(Layout):
    layoutUInames = []
    pyAppDimensions = [None, None]
   
    @classmethod
    def set(cls, mainWinRoot):
        mainWinRoot.geometry(str(cls.pyAppDimensions[0]) + "x" + str(cls.pyAppDimensions[1]))

        mon_windth, mon_height = _u.getMonitorSize()
        # vscode open
        ownerName, windowID, ownerPID = _u.getOwnersName_windowID_ofApp("vscode")
        cmd = oscr.getMoveWindowCMD(ownerPID, 
                                [mon_windth, mon_height , 0 , 0])
        subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).wait()




