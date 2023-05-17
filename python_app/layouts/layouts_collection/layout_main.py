
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
        if dt.AppState.CurrLayout != cls:
            ls.SectionLayout.close()      

        
        currSectionWPrefix = _upan.Current.Names.Section.name_wPrefix()
        currSection = _upan.Current.Names.Section.name()

        mon_width, mon_height = _u.getMonitorSize()
        mon_halfWidth = mon_width / 2
        mon_width, _ = _u.getMonitorSize()
        cls.pyAppDimensions = [int(mon_width / 2), 250]
        appWidth = cls.pyAppDimensions[0]
        appHeight = cls.pyAppDimensions[1]
        mon_width, mon_height = _u.getMonitorSize()
        mon_halfWidth = mon_width / 2
       
        #
        # SKIM
        #
        dimensions = [mon_halfWidth, mon_height, 0, 0]
    
        origMaterialBookFSPath_curr = _upan.Paths.OriginalMaterial.MainBook.getAbs()
        currMaterialName = fsf.Data.Book.currOrigMatName
        currMaterialFilename = \
            fsf.Wr.OriginalMaterialStructure.getOriginalMaterialsFilename(currMaterialName)
        skimFile_ID = currMaterialFilename

        currPage = fsf.Wr.OriginalMaterialStructure.getMaterialCurrPage(currMaterialName)

        oc.Wr.PdfApp.openPDF(origMaterialBookFSPath_curr, currPage)
        
        _, _, ownerPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.skim_ID, 
                                                        skimFile_ID)

        while ownerPID == None:
            sleep(0.1)
            _, _, ownerPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.skim_ID, 
                                                        skimFile_ID)

        cmd = oscr.getMoveWindowCMD(ownerPID, 
                                    dimensions,
                                    skimFile_ID)
        _u.runCmdAndWait(cmd)

        dt.OtherAppsInfo.Skim.main_pid = ownerPID

        # update the bounds
        if fsf.Wr.OriginalMaterialStructure.getMaterialPageSize(currMaterialName) == _u.Token.NotDef.list_t:
            fsf.Wr.OriginalMaterialStructure.setMaterialPageSize(currMaterialName)

        log.autolog("Opened skim!")

        #
        # FINDER
        #
        ownerPID = None
        subtractionNum = 30
        bounds = [mon_halfWidth, 
                  mon_height - appHeight - (subtractionNum + 30), 
                  appWidth, 
                  appHeight + (subtractionNum + 4 - 2)]

        currScreenshotFolderName = _upan.Current.Names.Section.Screenshot.name_wPrefix()


        if currSectionWPrefix == _u.Token.NotDef.str_t:
            log.autolog("No subssection to open yet.")
        else:
            currScreenshotDir = _upan.Paths.Screenshot.getAbs()
            oc.Wr.FsAppCalls.openFile(currScreenshotDir)
            
            _, _, ownerPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.finder_ID, 
                                                             currScreenshotFolderName)
            
            while ownerPID == None:
                sleep(0.1)
                _, _, ownerPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.finder_ID, 
                                                                currScreenshotFolderName)
            
            dt.OtherAppsInfo.Finder.main_pid = ownerPID
            
            if ownerPID == None: 
                log.autolog(currScreenshotFolderName)
                print("setMainLayout - Something went wrong. Finder could not open the folder")
            else:
                cmd = oscr.getMoveWindowCMD(ownerPID,
                                        bounds,
                                        currScreenshotFolderName)
                _u.runCmdAndWait(cmd)
            
            log.autolog("Moved Finder.")
        
        log.autolog("DONE setting section layout.")
        
        dt.AppState.CurrLayout = cls


    @classmethod
    def close(cls):
        currSection = _upan.Current.Names.Section.name()

        # close FS window
        _, _, ownerPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.finder_ID, 
                                                        currSection)
        if ownerPID != None:
            lm.LayoutsManager.closeFSWindow(currSection, ownerPID)
        else:
            log.autolog("Could not close the 'file system' window of the main layout")
        
        # close PDF reader window
        ownerPID = None
        
        currOrigMatName = fsf.Data.Book.currOrigMatName
        currOrigMatFilename = fsf.Wr.OriginalMaterialStructure.getOriginalMaterialsFilename(currOrigMatName)
        
        _, windowName, ownerPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.skim_ID, 
                                                                currOrigMatFilename)
        if ownerPID != None:
            fsf.Wr.OriginalMaterialStructure.updateOriginalMaterialPage(currOrigMatName)

            lm.LayoutsManager.closePDFwindow(currOrigMatFilename, ownerPID)
        else:
            log.autolog("Could not close the 'pdf reader' window of the main layout")
        
        log.autolog("Closed main layout")