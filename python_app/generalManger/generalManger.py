import os
import sys

import file_system.file_system_facade as fsf
import settings.facade as sf
import _utils.logging as log
import tex_file.tex_file_facade as tff
import _utils.pathsAndNames as _upan
import _utils._utils_main as _u

import data.constants as dc
import data.temp as dt

import outside_calls.outside_calls_facade as ocf

import daemon_service.daemon_service as ds

import layouts.layouts_facade as lf


class GeneralManger(dc.AppCurrDataAccessToken):
    daemonThread = None
    dserver = None

    @classmethod
    def startApp(cls):
        import UI.widgets_facade as wf
        # start the daemon to process client calls
        cls.daemonThread, cls.dserver = ds.startMainServerDaemon()

        # create startup menu
        log.autolog("-- Srartup started: ")
        messageMenuManager = wf.Wr.MenuManagers.MessageMenuManager()
        log.autolog("Started '{0}' UI manager".format("message menu"))
        mainMenuManager = wf.Wr.MenuManagers.MainMenuManager()
        log.autolog("Started '{0}' UI manager".format("main menu"))
        startupMenuManager = wf.Wr.MenuManagers.StartupMenuManager()
        log.autolog("Started '{0}' UI manager".format("startup menu"))
        tocMenuManager = wf.Wr.MenuManagers.TOCManager()
        log.autolog("Started '{0}' UI manager".format("toc menu"))

        startupMenuManager.showOnly()
        log.autolog("-- Srartup ended.")

        wf.Wr.WidgetWrappers.startLoop()

    @classmethod
    def exitApp(cls):
        import UI.widgets_facade as wf
        log.autolog("- Starting exiting the app")
        # main
        # mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
        #                                         wf.Wr.MenuManagers.MainMenuManager)
        # mainManager.winRoot.exitApp()

        # message
        mesManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                wf.Wr.MenuManagers.MessageMenuManager)
        mesManager.winRoot.exitApp()
        
        # startup
        stManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                wf.Wr.MenuManagers.StartupMenuManager)
        stManager.winRoot.exitApp()
        
        # toc
        tocManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                wf.Wr.MenuManagers.TOCManager)
        tocManager.winRoot.exitApp()

        lf.Wr.MainLayout.close()

        cls.dserver.close()
        cls.daemonThread.join()
        log.autolog("- Ended Exiting the app")
        sys.exit(0)

    def AddNewBook(bookName, bookPath, 
                   originalMaterialLocation, originalMaterialRelPath,
                   originalMaterialName):
        # update settings
        sf.Wr.Manager.Book.addNewBook(bookName, bookPath)
        
        # create filesystem
        addedNewbook = fsf.Wr.FileSystemManager.addNewBook(bookName, bookPath)        
        if not addedNewbook:
            message = "Could not create book at filepath" + bookPath
            log.autolog(message)
            return 

        # add original material   
        fsf.Wr.FileSystemManager.addOriginalMaterial(originalMaterialLocation, 
                                                    originalMaterialRelPath,
                                                    originalMaterialName)
    
    @classmethod
    def AddEntry(cls, subsection, imIdx:str, imText:str, addToTOC:bool, addToTOCwIm:bool):
        import UI.widgets_facade as wf

        imagePath_curr = os.path.join(_upan.Paths.Screenshot.getAbs(),
                                    _upan.Names.getImageName(str(imIdx), subsection))
        
        imID = imIdx
        linkDict = fsf.Data.Sec.imLinkDict(subsection)
        imGlobalLinksDict = fsf.Data.Sec.imGlobalLinksDict(subsection)
        
        if (imID in list(linkDict.values())):
            messManager = dt.AppState.UIManagers.getData(cls.appCurrDataAccessToken,
                                                        wf.Wr.MenuManagers.MessageMenuManager)
            mathManager = dt.AppState.UIManagers.getData(cls.appCurrDataAccessToken,
                                                        wf.Wr.MenuManagers.MainMenuManager)
            response = messManager.show("The index '{0}' already exists. Do you want to update?".format(imID), True)
            
            if response:
                names = []
                for name, id in linkDict.items():
                    if id == imID:
                        #remove the image
                        prevImagePath_curr = os.path.join(_upan.Paths.Screenshot.getAbs(),
                                        _upan.Names.getImageName(str(imIdx), subsection) + ".png")
                        ocf.Wr.FsAppCalls.deleteFile(prevImagePath_curr)

                        names.append(name)
                
                for name in names:
                    linkDict.pop(name, None)
                
                fsf.Data.Sec.imLinkDict(subsection, linkDict)

                if imGlobalLinksDict == _u.Token.NotDef.dict_t:
                    imGlobalLinksDict = {}

                imGlobalLinksDict[imIdx] = _u.Token.NotDef.dict_t
                fsf.Data.Sec.imGlobalLinksDict(subsection, imGlobalLinksDict)
            
            mathManager.show()
            
            if not response:
                return False
        

        # ADD CONTENT ENTRY TO THE PROCESSED CHAPTER
        tff.Wr.TexFileModify.addProcessedImage(subsection, imIdx, imText)

        if addToTOC:
            if addToTOCwIm:
                # TOC ADD ENTRY WITH IMAGE
                tff.Wr.TexFileModify.addImageLinkToTOC_wImage(subsection, imIdx, imText)
            else:  
                # TOC ADD ENTRY WITHOUT IMAGE
                tff.Wr.TexFileModify.addImageLinkToTOC_woImage(subsection, imIdx, imText)
        

        # STOTE IMNUM, IMNAME AND LINK
        fsf.Wr.SectionCurrent.setImLinkAndIDX(imText, imIdx)
        
        # POPULATE THE MAIN FILE
        tff.Wr.TexFilePopulate.populateCurrMainFile()
        
        # take a screenshot
        if ocf.Wr.FsAppCalls.checkIfImageExists(imagePath_curr):
            mesManager = dt.AppState.UIManagers.getData(cls.appCurrDataAccessToken, 
                                                        wf.Wr.MenuManagers.MessageMenuManager)
            
            response = mesManager.show("The image with idx '{0}' already exists. Overrite", True)
            
            if response:
                ocf.Wr.ScreenshotCalls.takeScreenshot(imagePath_curr)
            else:
                return False
        else:
            ocf.Wr.ScreenshotCalls.takeScreenshot(imagePath_curr)
        
        # ORIGINAL MATERIAL DATA
        origMatName = fsf.Data.Book.currOrigMatName
        fsf.Wr.OriginalMaterialStructure.updateOriginalMaterialPage(origMatName)

        page = fsf.Wr.OriginalMaterialStructure.getMaterialCurrPage(origMatName)

        if fsf.Data.Sec.origMatName == _u.Token.NotDef.str_t:
            fsf.Data.Sec.origMatName(subsection, origMatName)

        pagesDict = fsf.Data.Sec.imLinkOMPageDict(subsection)

        if pagesDict == _u.Token.NotDef.dict_t:
            pagesDict = {}

        pagesDict[imIdx] = page
        fsf.Data.Sec.imLinkOMPageDict(subsection, pagesDict)

        # ADD LINK TO THE ORIGINAL MATERIAL
        numNotesOnThePage = str(len([i for i in list(pagesDict.values()) if i == page]))
        currOMName = fsf.Data.Book.currOrigMatName
        bookName = sf.Wr.Manager.Book.getCurrBookName()
        currTopSection = fsf.Data.Book.currTopSection
        noteUrl = tff.Wr.TexFileUtils.getUrl(bookName, currTopSection, subsection, imIdx, "full")
        fsf.Wr.OriginalMaterialStructure.addNoteToOriginalMaterial(currOMName, page, noteUrl, numNotesOnThePage)
