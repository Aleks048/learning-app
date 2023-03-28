import os, subprocess
from time import sleep


import layouts.layouts_collection.layout_main as lma
import layouts.layouts_manager as lm

import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import _utils.logging as log
import tex_file.tex_file_facade as tf
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

        if  dt.AppState.CurrLayout != cls:
            lma.MainLayout.close()

        pathToSourceFolder = _upan.Current.Paths.Section.abs()
        currSection = _upan.Current.Names.Section.name()
        
        # check if the folder is empty.
        if len(os.listdir(_upan.Current.Paths.Screenshot.abs())) == 0: 
            msg = "No images yet. Can't switch to section."
            
            wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)
            
            mainMenuManager = dt.AppState.UIManagers.getData(cls.appCurrDataAccessToken, 
                                                        wf.Wr.MenuManagers.MainMenuManager.__base__)
            
            mainMenuManager.switchToMainLayout()

            lma.MainLayout.set()
            log.autolog(msg)
            return
        else:
            ocf.Wr.LatexCalls.buildCurrentSubsectionPdf()

            # check if PDF exists
            while not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(_upan.Current.Paths.PDF.abs()):
                sleep(0.1)


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

        # create the layout in the vscode window
        conterntFilepath = _upan.Current.Paths.TexFiles.Content.abs()
        TOCFilepath = _upan.Current.Paths.TexFiles.TOC.abs()

        # move vscode files to desired lines
        currImIdx = fsf.Wr.SectionCurrent.getImIDX()
        currBookName = sf.Wr.Manager.Book.getCurrBookName()
        currSecWPrefix =  _upan.Current.Names.Section.name_wPrefix()
        conLine = tf.Wr.TexFileProcess.getConLine(currBookName, currSecWPrefix, currSection, currImIdx)
        tocLine = tf.Wr.TexFileProcess.getTocLine(currBookName, currSecWPrefix, currSection, currImIdx)

        ocf.Wr.IdeCalls.openNewTab(TOCFilepath, tocLine)
        sleep(0.3)
        ocf.Wr.IdeCalls.openNewTab(conterntFilepath, conLine)

        # cmd = oscr.get_SetSecVSCode_CMD()
        # _u.runCmdAndWait(cmd)

        log.autolog("set VSCODE section.")
        
        log.autolog("DONE setting section layout.")

        dt.AppState.CurrLayout = cls

    @classmethod
    def close(cls):
        currSection = fsf.Wr.SectionCurrent.getSectionNameNoPrefix()

        #close the subsection VSCode if it is open
        if dt.OtherAppsInfo.VsCode.section_pid != _u.Token.NotDef.str_t:
            lm.LayoutsManager.closeIDEWindow(currSection, dt.OtherAppsInfo.VsCode.section_pid)
        #close the subsection Skim if it is open
        if dt.OtherAppsInfo.Skim.section_pid != _u.Token.NotDef.str_t:
            lm.LayoutsManager.closePDFwindow(currSection, dt.OtherAppsInfo.Skim.section_pid)
        
        log.autolog("Closed section layout!")