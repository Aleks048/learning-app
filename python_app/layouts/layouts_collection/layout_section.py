import os, subprocess
from time import sleep
from threading import Thread

import layouts.layouts_utils as lu
import layouts.layouts_collection.layout_main as lm

import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import _utils.logging as log
# import UI.widgets_facade as wm
import tex_file.tex_file_facade as tm
import file_system.file_system_facade as fsm
import scripts.osascripts as oscr

import settings.facade as sf

import layouts.layouts_common as lc
import outside_calls.outside_calls_facade as ocf

import data.constants as dc
import data.temp as dt

import UI.widgets_facade as wf

class SectionLayout(lc.Layout,
                    dc.AppCurrDataAccessToken):
    layoutUInames = []
    pyAppDimensions = [None, None]    

    @classmethod
    def set(cls, mainWinRoot = None, menuWidth = 0, menuHeight = 55):
        '''
        # Section: 
        #       skim Section to the right 
        #       vscode to the left
        '''

        pathToSourceFolder = _upan.Current.Paths.Section.abs()
        currSection = _upan.Current.Names.Section.name()
        
        if dt.OtherAppsInfo.Finder.main_pid != _u.Token.NotDef.str_t:
            cmd = oscr.closeFinderWindow(dt.OtherAppsInfo.Finder.main_pid, currSection)
            subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).wait()
        
        if dt.OtherAppsInfo.Skim.main_pid != _u.Token.NotDef.str_t:
            _, windowName, ownerPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.skim_ID, 
                                                        sf.Wr.Data.TokenIDs.Misc.wholeBook_ID + ".pdf")
            if windowName != None:
                dt.OtherAppsInfo.Skim.main_winName = windowName
                page = windowName.split("page ")
                if len(page) != 2:
                    log.autolog("setSectionLayout - Something went wrong. Can't get page number out of the name.")
                    return
                else:
                    page = page[-1]
                
                if type(page) == str:
                    page = page.split(" ")[0]
                    fsm.Data.Book.currentPage = page
                    
                    cmd = oscr.closeSkimDocument(dt.OtherAppsInfo.Skim.main_pid, 
                                                 sf.Wr.Data.TokenIDs.Misc.wholeBook_ID)
                    subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).wait()


        
        # check if the folder is empty.
        if len(os.listdir(_upan.Current.Paths.Screenshot.abs())) == 0: 
            msg = "No images yet. Can't switch to section."
            messsageMenuManager = dt.AppState.UIManagers.getData(cls.appCurrDataAccessToken, 
                                                        wf.Wr.MenuManagers.MessageMenuManager)
            response = messsageMenuManager.show(msg, True)
            
            mainMenuManager = dt.AppState.UIManagers.getData(cls.appCurrDataAccessToken, 
                                                        wf.Wr.MenuManagers.MainMenuManager.__base__)
            
            mainMenuManager.switchToMainLayout()

            lm.MainLayout.set()
            log.autolog(msg)
            return
        else:
            ocf.Wr.LatexCalls.buildCurrentSubsectionPdf()

 
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

        pathToCurrSecPDF = _upan.Current.Paths.PDF.abs()
        
        if ownerPID == None:
            cmd = " open skim://" + pathToCurrSecPDF
            subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).wait()

        while ownerPID == None:
            _, _, ownerPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.skim_ID, currSection)
            sleep(0.1)

        dt.OtherAppsInfo.Skim.section_pid = ownerPID
        
        skimBounds = [mon_halfWidth, mon_height - menuHeight - 80, mon_halfWidth, menuHeight + 90]
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
            _, _, ownerPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.vsCode_ID, currSection)
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
        conterntFilepath = _upan.Current.Paths.TexFiles.Content.abs()
        TOCFilepath = _upan.Current.Paths.TexFiles.TOC.abs()
        
        cmd = oscr.get_SetSecVSCode_CMD()
        subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).wait()

        cmd = "code " + TOCFilepath + " " + conterntFilepath
        subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).wait()
        log.autolog("moved VSCODE.")
        
        log.autolog("DONE setting section layout.")

