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

    currFileNum = 0

    @classmethod
    def set(cls, menuHeight = 55, imIdx = _u.Token.NotDef.str_t):
        '''
        # Section: 
        #       skim Section to the right 
        #       vscode to the left
        '''

        currBookName = sf.Wr.Manager.Book.getCurrBookName()
        currBookpath = sf.Wr.Manager.Book.getPathFromName(currBookName)
        subsection = fsf.Data.Book.currSection

        if  imIdx == _u.Token.NotDef.str_t:
            imIdx = fsf.Wr.Links.ImIDX.get_curr()

        if  dt.AppState.CurrLayout != cls:
            log.autolog("Will close the section layout.")
            lma.MainLayout.close()

        pathToSourceFolder_curr = _upan.Paths.Section.getAbs()
        currSection = _upan.Current.Names.Section.name()
        
        # check if the folder is empty.
        if len(os.listdir(_upan.Paths.Screenshot.getAbs())) == 0: 
            msg = "No images yet. Can't switch to section."
            
            wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)
            
            mainMenuManager = dt.AppState.UIManagers.getData(cls.appCurrDataAccessToken, 
                                                        wf.Wr.MenuManagers.MainMenuManager.__base__)
            
            mainMenuManager.switchToMainLayout()

            lma.MainLayout.set()
            log.autolog(msg)
            return
        else:
            ocf.Wr.LatexCalls.buildPDF(currBookpath, subsection, imIdx)

            # check if curr subsection PDF exists
            while not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(_upan.Paths.PDF.getAbs(currBookpath, subsection, imIdx)):
                sleep(0.1)


        mon_width, mon_height = _u.getMonitorSize()
        mon_halfWidth = mon_width / 2

        #
        # VSCODE
        #

        ocf.Wr.IdeCalls.openNewWindow(pathToSourceFolder_curr)
        sleep(0.5)

        # create the layout in the vscode window
        conterntFilepath_curr = _upan.Paths.TexFiles.Content.getAbs(idx = imIdx)
        TOCFilepath_curr = _upan.Paths.TexFiles.TOC.getAbs(idx = imIdx)

        conLine = tf.Wr.TexFileProcess.getConLine(currBookName, subsection, imIdx)
        tocLine = tf.Wr.TexFileProcess.getTocLine(currBookName, subsection, imIdx)

        ocf.Wr.IdeCalls.openNewTab(TOCFilepath_curr, tocLine)
        sleep(0.3)
        ocf.Wr.IdeCalls.openNewTab(conterntFilepath_curr, conLine)

        ownerPID = None
        vscodefileMarker = \
            _upan.Names.getSubsectionFilesEnding(imIdx) + ".tex" if imIdx != _u.Token.NotDef.str_t else currSection
        _, _, ownerPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.vsCode_ID, vscodefileMarker)
        
        while ownerPID == None:
            sleep(0.1)
            _, _, ownerPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.vsCode_ID, vscodefileMarker)
        
        dt.OtherAppsInfo.VsCode.section_pid  = ownerPID

        vscodeBounds = [mon_halfWidth, mon_height , 0, 0]
        vscodeBounds  = [str(i) for i in vscodeBounds]
        # move vscode into position
        cmd = oscr.getMoveWindowCMD(ownerPID,
                                vscodeBounds,
                                vscodefileMarker)
        _u.runCmdAndWait(cmd)
        
        # cmd = oscr.get_SetSecVSCode_CMD()
        # _u.runCmdAndWait(cmd)
        
        log.autolog("moved VSCODE.")

        #
        # SKIM
        #
        skimfileMarker = _upan.Names.getSubsectionFilesEnding(imIdx) + ".pdf"
        _, _, ownerPID = _u.getOwnersName_windowID_ofApp("skim", skimfileMarker)
        dt.OtherAppsInfo.Skim.section_pid = ownerPID
        
        ocf.Wr.PdfApp.openSubsectionPDF(str(int(imIdx) - (int(imIdx) % 5)), 
                                        subsection, 
                                        currBookName)

        # Move skim
        while ownerPID == None:
            _, _, ownerPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.skim_ID, skimfileMarker)
            sleep(0.1)

        dt.OtherAppsInfo.Skim.section_pid = ownerPID
        cls.currFileNum = _upan.Names.getSubsectionFilesEnding(imIdx)
        
        skimBounds = [mon_halfWidth, mon_height - menuHeight - 120, mon_halfWidth, menuHeight + 90]
        cmd = oscr.getMoveWindowCMD(ownerPID,
                                skimBounds,
                                skimfileMarker)
        _u.runCmdAndWait(cmd)

        sleep(0.3)
        ocf.Wr.PdfApp.openSubsectionPDF(imIdx, subsection, currBookName)
        log.autolog("moved SKIM")


        log.autolog("set VSCODE section.")
        
        log.autolog("DONE setting section layout.")

        dt.AppState.CurrLayout = cls

    @classmethod
    def close(cls):
        currSection = fsf.Data.Book.currSection

        # pdfMarker = str(cls.currFileNum) + ".pdf"
        # ideMarker = str(cls.currFileNum) + ".tex"

        #close the subsection VSCode if it is open
        if dt.OtherAppsInfo.VsCode.section_pid != _u.Token.NotDef.str_t:
            lm.LayoutsManager.closeIDEWindow(currSection, dt.OtherAppsInfo.VsCode.section_pid)
        #close the subsection Skim if it is open
        if dt.OtherAppsInfo.Skim.section_pid != _u.Token.NotDef.str_t:
            lm.LayoutsManager.closePDFwindow(currSection, dt.OtherAppsInfo.Skim.section_pid)
        
        lm.LayoutsManager.closeNoteAppWindow(currSection)
        
        log.autolog("Closed section layout!")