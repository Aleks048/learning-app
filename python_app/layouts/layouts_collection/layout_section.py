import os, subprocess
from time import sleep
from threading import Thread

import layouts.layouts_utils as lu
import layouts.layouts_collection.layout_main as lm

import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import _utils.logging as log
import tex_file.tex_file_facade as tm
import file_system.file_system_facade as fsm
import scripts.osascripts as oscr

import settings.facade as sf

import layouts.layouts_common as lc
import outside_calls.outside_calls_facade as ocf

import data.constants as dc
import data.temp as dt

import UI.widgets_facade as wf
import file_system.file_system_facade as fsf

class SectionLayout(lc.Layout,
                    dc.AppCurrDataAccessToken):
    layoutUInames = []
    pyAppDimensions = [None, None]    

    @classmethod
    def set(cls, menuHeight = 55):
        '''
        # Section: 
        #       skim Section to the right 
        #       vscode to the left
        '''

        lm.MainLayout.close()

        pathToSourceFolder = _upan.Current.Paths.Section.abs()
        currSection = _upan.Current.Names.Section.name()
        
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


        mon_width, mon_height = _u.getMonitorSize()
        mon_halfWidth = mon_width / 2
 
        #
        # SKIM
        #
        _, _, ownerPID = _u.getOwnersName_windowID_ofApp("skim", currSection)
        dt.OtherAppsInfo.Skim.section_pid = ownerPID

        pathToCurrSecPDF = _upan.Current.Paths.PDF.abs()
        
        if ownerPID == None:
            ocf.Wr.PdfApp.openPDF(pathToCurrSecPDF)

        while ownerPID == None:
            _, _, ownerPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.skim_ID, currSection)
            sleep(0.1)

        dt.OtherAppsInfo.Skim.section_pid = ownerPID
        
        skimBounds = [mon_halfWidth, mon_height - menuHeight - 120, mon_halfWidth, menuHeight + 90]
        cmd = oscr.getMoveWindowCMD(ownerPID,
                                skimBounds,
                                currSection)
        subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).wait()
        log.autolog("moved SKIM")


        #
        # VSCODE
        #
        ocf.Wr.IdeCalls.openNewWindow(pathToSourceFolder)

        ownerPID = None
        _, _, ownerPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.vsCode_ID, currSection)
        
        while ownerPID == None:
            sleep(0.1)
            _, _, ownerPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.vsCode_ID, currSection)
        
        dt.OtherAppsInfo.VsCode.section_pid  = ownerPID

        vscodeBounds = [mon_halfWidth, mon_height , 0, 0]
        vscodeBounds  = [str(i) for i in vscodeBounds]
        # move vscode into position
        cmd = oscr.getMoveWindowCMD(ownerPID,
                                vscodeBounds,
                                currSection)
        _u.runCmdAndWait(cmd)
        log.autolog("moved VSCODE.")

        # # create the layout in the vscode window
        conterntFilepath = _upan.Current.Paths.TexFiles.Content.abs()
        TOCFilepath = _upan.Current.Paths.TexFiles.TOC.abs()
        
        cmd = oscr.get_SetSecVSCode_CMD()
        subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).wait()

        ocf.Wr.IdeCalls.openNewTab(conterntFilepath + " " + TOCFilepath)
        log.autolog("set VSCODE section.")
        
        log.autolog("DONE setting section layout.")

    @classmethod
    def close(cls):
        currSection = fsf.Wr.SectionCurrent.getSectionNameNoPrefix()

        #close the subsection VSCode if it is open
        if dt.OtherAppsInfo.VsCode.section_pid != _u.Token.NotDef.str_t:
            cmd = oscr.closeVscodeWindow(dt.OtherAppsInfo.VsCode.section_pid, currSection)
            _u.runCmdAndWait(cmd)
        #close the subsection Skim if it is open
        if dt.OtherAppsInfo.Skim.section_pid != _u.Token.NotDef.str_t:
            cmd = oscr.closeSkimDocument(dt.OtherAppsInfo.Skim.section_pid, currSection)
            _u.runCmdAndWait(cmd)
        
        log.autolog("Closed section layout!")