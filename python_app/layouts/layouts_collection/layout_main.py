
from time import sleep

import layouts.layouts_collection.layout_section as ls

import _utils._utils_main as _u
import _utils.logging as log
import _utils.pathsAndNames as _upan
import tex_file.tex_file_facade as tm
import file_system.file_system_facade as fsf
import data.temp as dt
import scripts.osascripts as oscr
import outside_calls.outside_calls_facade as oc

import layouts.layouts_common as lc
import layouts.layouts_manager as lm
import settings.facade as sf

class MainLayout(lc.Layout):
    layoutUInames = []
    pyAppDimensions = [None, None]
    
    @classmethod
    def set(cls):
        '''
        # main:
        #       full book to the left
        #       vscode/finder(with images folder) to the right
        '''

        log.autolog("-- Starting main layout")

        log.autolog("--- Starting closing other layout")
        
        if "section" in dt.AppState.CurrLayout.__name__.lower():
            ls.SectionLayout.close()      
        
        log.autolog("--- Ended closing other layout")

        currSection = _upan.Current.Names.Section.name()

        mon_width, mon_height = _u.getMonitorSize()
        mon_halfWidth = mon_width / 2
        mon_width, _ = _u.getMonitorSize()
        cls.pyAppDimensions = [int(mon_width / 2), 550]
        appWidth = cls.pyAppDimensions[0]
        appHeight = cls.pyAppDimensions[1]
        mon_width, mon_height = _u.getMonitorSize()
        mon_halfWidth = mon_width / 2
       
        
        #
        # SKIM
        #
        log.autolog("--- Starting pdf app manipulation")
        dimensions = [mon_halfWidth, mon_height, 0, 0]
    
        OMName = fsf.Data.Book.currOrigMatName
        origMaterialBookFSPath_curr = fsf.Wr.OriginalMaterialStructure.getMaterialPath(OMName)

        currPage = fsf.Wr.OriginalMaterialStructure.getMaterialCurrPage(OMName)
        oc.Wr.PdfApp.openPDF(origMaterialBookFSPath_curr, currPage)

        zoomLevel = fsf.Wr.OriginalMaterialStructure.getMaterialZoomLevel(OMName)
        pdfToken:str = origMaterialBookFSPath_curr.split("/")[-1].replace(".pdf", "")
        cmd = oscr.setDocumentScale(pdfToken, zoomLevel)
        _u.runCmdAndWait(cmd)

        pdfAppFile_ID = \
            fsf.Wr.OriginalMaterialStructure.getOriginalMaterialsFilename(OMName)
        
        _, _, ownerPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.skim_ID, 
                                                        pdfAppFile_ID)

        while ownerPID == None:
            sleep(0.1)
            _, _, ownerPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.skim_ID, 
                                                        pdfAppFile_ID)

        cmd = oscr.getMoveWindowCMD(ownerPID, 
                                    dimensions,
                                    pdfAppFile_ID)
        _u.runCmdAndWait(cmd)

        dt.OtherAppsInfo.Skim.main_pid = ownerPID

        # update the bounds
        if fsf.Wr.OriginalMaterialStructure.getMaterialPageSize(OMName) == [-1, -1]:
            fsf.Wr.OriginalMaterialStructure.setMaterialPageSize(OMName)

        log.autolog("--- Ended Pdf app manipulation. Opened skim!")

        #
        # FINDER
        #
        # log.autolog("--- Starting file system manipulation")
        # ownerPID = None
        # subtractionNum = 30
        # bounds = [int(mon_halfWidth), 
        #           mon_height - appHeight - (subtractionNum + 30), 
        #           appWidth, 
        #           appHeight + (subtractionNum + 4 - 2)]

        # currScreenshotFolderName = _upan.Current.Names.Section.Screenshot.name_wPrefix()

        # if currSection == _u.Token.NotDef.str_t:
        #     log.autolog("No subssection to open yet.")
        # else:
        #     currScreenshotDir = _upan.Paths.Screenshot.getAbs()
        #     oc.Wr.FsAppCalls.openFile(currScreenshotDir)
            
        #     _, _, ownerPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.finder_ID, 
        #                                                      currScreenshotFolderName)
            
        #     while ownerPID == None:
        #         sleep(0.1)
        #         _, _, ownerPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.finder_ID, 
        #                                                         currScreenshotFolderName)
            
        #     dt.OtherAppsInfo.Finder.main_pid = ownerPID
            
        #     if ownerPID == None: 
        #         log.autolog(currScreenshotFolderName)
        #         print("setMainLayout - Something went wrong. Finder could not open the folder")
        #     else:
        #         cmd = oscr.getMoveWindowCMD(ownerPID,
        #                                 bounds,
        #                                 currScreenshotFolderName)
        #         _u.runCmdAndWait(cmd)
            
        #     log.autolog("Moved fs window.")
        
        log.autolog("--- File system manipulation ended.")
        
        dt.AppState.CurrLayout = cls
        log.autolog("-- Ended main layout setting")


    @classmethod
    def close(cls):
        log.autolog("-- Starting closing of main layout")

        currSection = _upan.Current.Names.Section.name()

        # close FS window
        
        # log.autolog("--- Starting closing of 'FS'")
        # _, _, ownerPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.finder_ID, 
        #                                                 currSection)

        # if ownerPID != None:
        #     lm.LayoutsManager.closeFSWindow(currSection, ownerPID)
        # else:
        #     log.autolog("Could not close the 'file system' window of the main layout")
        
        # log.autolog("--- Ended closing of 'FS'")
        
        # close PDF reader window
        log.autolog("--- Starting closing of 'PDF editor'")
        ownerPID = None
        
        currOrigMatName = fsf.Data.Book.currOrigMatName
        currOrigMatFilename:str = fsf.Wr.OriginalMaterialStructure.getOriginalMaterialsFilename(currOrigMatName)
        
        _, windowName, ownerPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.skim_ID, 
                                                                currOrigMatFilename)
        if ownerPID != None:
            fsf.Wr.OriginalMaterialStructure.updateOriginalMaterialPage(currOrigMatName)

            lm.LayoutsManager.closePDFwindow(currOrigMatFilename, ownerPID)
        else:
            log.autolog("Could not close the 'pdf reader' window of the main layout")
        
        log.autolog("--- Ended closing of 'PDF editor'")
        

        log.autolog("-- Ended closing of main layout")