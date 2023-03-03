import os, subprocess
from time import sleep
from threading import Thread

import layouts.layouts_utils as lu

import _utils._utils_main as _u
import _utils.logging as log
# import UI.widgets_facade as wm
import tex_file.tex_file_facade as tm
import file_system.file_system_facade as fsm
import data.temp as dt
import scripts.osascripts as oscr

import layouts.layouts_common as lc

class SectionLayout(lc.Layout):
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
        # if len(os.listdir(os.path.join(pathToSourceFolder, secPrefix + "_" + currSection + "_images"))) == 0:
        #     msg = "No images yet. Can't switch to section."
        #     wm.Wr.MessageMenu.createMenu(msg)
        #     log.autolog(msg)
        #     return
        # else:
        #     # rebuild the section doc
        #     # NOTE: do we need a rebuild each time we switch??
        #     wm.Data.UItkVariables.needRebuild.set(True)
        
        # if wm.Data.UItkVariables.needRebuild.get() == True:
        #     _waitDummy = tm.Wr.TexFile.buildCurrentSubsectionPdf()

 
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

