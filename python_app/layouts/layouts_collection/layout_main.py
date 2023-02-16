
import os, subprocess
from time import sleep
from threading import Thread

import layouts.layouts_utils as lu

import _utils._utils_main as _u
import _utils.logging as log
import UI.widgets_facade as wf
import tex_file.tex_file_facade as tm
import file_system.file_system_manager as fsm
import data.temp as dt
import scripts.osascripts as oscr
import outside_calls.outside_calls_facade as oc

import layouts.layouts_common as lc

class MainLayout(lc.Layout):
    layoutUInames = []
    pyAppDimensions = [None, None]
    
    @classmethod
    def set(cls, mainWinRoot, appWidth, appHeight):
        '''
        # main:
        #       full book to the left
        #       vscode/finder(with images folder) to the right
        '''

        currSection = fsm.Wr.SectionCurrent.readCurrSection()

        #close the subsection VSCode if it is open
        if dt.OtherAppsInfo.VsCode.section_pid != _u.Token.NotDef.str_t:
            cmd = oscr.closeVscodeWindow(dt.OtherAppsInfo.VsCode.section_pid, currSection)
            subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).wait()
        #close the subsection Skim if it is open
        if dt.OtherAppsInfo.Skim.section_pid != _u.Token.NotDef.str_t:
            cmd = oscr.closeSkimDocument(dt.OtherAppsInfo.Skim.section_pid, currSection)
            subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).wait()

        mon_width, mon_height = _u.getMonitorSize()
        mon_halfWidth = mon_width / 2

        # wm.Data.UItkVariables.needRebuild.set(False)
        # change the menu size
        mainWinRoot.geometry(str(appWidth) + "x" + str(appHeight) 
                            + "+" + str(int(mon_halfWidth)) + "+0")
        # switch menu
        wf.Wr.MenuManagers.MainMenuManager.LayoutManagers.Main.show() 
       
        #
        # SKIM
        #
        dimensions = [mon_halfWidth, mon_height, 0, 0]
    
        origMaterialBookFSPath = fsm.Wr.Paths.OriginalMaterial.MainBook.getCurrAbs()
        
        currPage = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.currentPage_ID)

        oc.Wr.PdfApp.openPDF(origMaterialBookFSPath, currPage)
        
        _, _, ownerPID = _u.getOwnersName_windowID_ofApp(_u.Settings._appsIDs.skim_ID, 
                                                        _u.Settings.PubProp.wholeBook_ID + ".pdf")
        while ownerPID == None:
            _, _, ownerPID = _u.getOwnersName_windowID_ofApp(_u.Settings._appsIDs.skim_ID, 
                                                            _u.Settings.PubProp.wholeBook_ID + ".pdf")
            log.autolog("Opening skim...")
            sleep(0.1)

        if ownerPID == None: 
            log.autolog("Something went wrong. Skim could not open the document")
        else:
            cmd = oscr.getMoveWindowCMD(ownerPID, 
                                        dimensions,
                                        _u.Settings.PubProp.wholeBook_ID)
            subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).wait()

        dt.OtherAppsInfo.Skim.main_pid = ownerPID
        log.autolog("Opened skim!")

        #
        # FINDER
        #
        bounds = [mon_halfWidth, mon_height - appHeight - 80, appWidth, appHeight + 54]

        currSectionWPrefix = fsm.Wr.SectionCurrent.getSectionNameWprefix()
        if currSectionWPrefix == _u.Token.NotDef.str_t:
            log.autolog("No subssection to open yet.")
        else:
            _, _, ownerPID = _u.getOwnersName_windowID_ofApp("finder", currSectionWPrefix + "_images")
            dt.OtherAppsInfo.Finder.main_pid = ownerPID
            
            if ownerPID == None:
                # if no window found we open one with the chapter in Finder
                currScreenshotDir = fsm.Wr.Paths.Screenshot.getAbs_curr()
                oc.Wr.fsAppCalls.openFile(currScreenshotDir)
            
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
