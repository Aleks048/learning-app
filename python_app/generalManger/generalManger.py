import os
import sys
import re
import time

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
import scripts.osascripts as oscr


class GeneralManger(dc.AppCurrDataAccessToken):
    daemonThread = None
    dserver = None

    @classmethod
    def startNonStartMenus(cls):
        import UI.widgets_facade as wf
        # start the daemon to process client calls
        cls.daemonThread, cls.dserver = ds.startMainServerDaemon()

        # create startup menu
        log.autolog("-- Srartup of other menus started: ")
        messageMenuManager = wf.Wr.MenuManagers.MessageMenuManager()
        log.autolog("Started '{0}' UI manager".format("message menu"))
        mainMenuManager = wf.Wr.MenuManagers.MathMenuManager()
        log.autolog("Started '{0}' UI manager".format("main menu"))
        tocMenuManager = wf.Wr.MenuManagers.TOCManager()
        log.autolog("Started '{0}' UI manager".format("toc menu"))
        log.autolog("-- Srartup  of other menus ended.")

        mainMenuManager.showOnly()


    @classmethod
    def startApp(cls):
        import UI.widgets_facade as wf
        # start the daemon to process client calls 

        log.autolog("-- Srartup startup menu started: ")
        startupMenuManager = wf.Wr.MenuManagers.StartupMenuManager()
        log.autolog("Started '{0}' UI manager".format("startup menu"))

        startupMenuManager.showOnly()
        log.autolog("-- Srartup of startup menu ended.")

        wf.Wr.WidgetWrappers.startLoop()

    @classmethod
    def exitApp(cls):
        import UI.widgets_facade as wf
        log.autolog("- Starting exiting the app")

        # Updating the remote
        msg = "Closing the book."
        ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)

        # main
        mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                wf.Wr.MenuManagers.MathMenuManager)
        mainManager.winRoot.exitApp()

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
                   originalMaterialName,
                   bookRemoteAddress):
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
        
        # init the tracking system
        ocf.Wr.TrackerAppCalls.initBook(bookPath, bookRemoteAddress)
    
    @classmethod
    def AddEntry(cls, subsection, imIdx:str, imText:str, addToTOC:bool, addToTOCwIm:bool):
        import UI.widgets_facade as wf

        imagePath_curr = os.path.join(_upan.Paths.Screenshot.getAbs(),
                                    _upan.Names.getImageName(str(imIdx), subsection))
        
        # take a screenshot
        if ocf.Wr.FsAppCalls.checkIfImageExists(imagePath_curr):
            mesManager = dt.AppState.UIManagers.getData(cls.appCurrDataAccessToken, 
                                                        wf.Wr.MenuManagers.MessageMenuManager)
            
            response = mesManager.show("The image with idx '{0}' already exists.\n Overrite?".format(imIdx), True)
            
            if response:
                ocf.Wr.ScreenshotCalls.takeScreenshot(imagePath_curr)

            mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken", 
                                                   wf.Wr.MenuManagers.MathMenuManager)

            mainManager.show()

            if not response:
                return
        else:
            ocf.Wr.ScreenshotCalls.takeScreenshot(imagePath_curr)

        timer = 1

        while not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(imagePath_curr + ".png"):
            time.sleep(0.3)
            timer += 1

            if timer > 50:
                return False

        imID = imIdx
        linkDict = fsf.Data.Sec.imLinkDict(subsection)
        imGlobalLinksDict = fsf.Data.Sec.imGlobalLinksDict(subsection)
        
        if (imID in list(linkDict.values())):
            messManager = dt.AppState.UIManagers.getData(cls.appCurrDataAccessToken,
                                                        wf.Wr.MenuManagers.MessageMenuManager)
            mathManager = dt.AppState.UIManagers.getData(cls.appCurrDataAccessToken,
                                                        wf.Wr.MenuManagers.MathMenuManager)
            response = messManager.show("The index '{0}' already exists.\n Do you want to update?".format(imID), True)
            
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

        # STOTE IMNUM, IMNAME AND LINK
        fsf.Wr.SectionCurrent.setImLinkAndIDX(imText, imIdx)
        
        # ORIGINAL MATERIAL DATA
        origMatName = fsf.Data.Book.currOrigMatName

        fsf.Wr.OriginalMaterialStructure.updateOriginalMaterialPage(origMatName)

        page = fsf.Wr.OriginalMaterialStructure.getMaterialCurrPage(origMatName)

        origMatNameDict = {}

        if fsf.Data.Sec.origMatNameDict(subsection) != _u.Token.NotDef.dict_t:
            origMatNameDict = fsf.Data.Sec.origMatNameDict(subsection)

        origMatNameDict[imIdx] = origMatName
        fsf.Data.Sec.origMatNameDict(subsection, origMatNameDict)

        pagesDict = fsf.Data.Sec.imLinkOMPageDict(subsection)

        if pagesDict == _u.Token.NotDef.dict_t:
            pagesDict = {}

        pagesDict[imIdx] = page
        fsf.Data.Sec.imLinkOMPageDict(subsection, pagesDict)

        # toc w image
        tocWImageDict = fsf.Data.Sec.tocWImageDict(subsection)

        if tocWImageDict == _u.Token.NotDef.dict_t:
            tocWImageDict = {}
        
        tocWImageDict[imIdx] = "1" if addToTOCwIm else "0"
        fsf.Data.Sec.tocWImageDict(subsection, tocWImageDict)

        # images group
        imagesGroupList = list(fsf.Data.Sec.imagesGroupsList(subsection).keys())
        imagesGroupDict = fsf.Data.Sec.imagesGroupDict(subsection)

        if imagesGroupDict == _u.Token.NotDef.dict_t:
            imagesGroupDict = {}

        if imagesGroupDict != {}:
            if not dt.AppState.UseLatestGroup.getData(cls.appCurrDataAccessToken):
                lastGroup = int(list(imagesGroupDict.values())[-1])
            else:
                lastGroup = len(imagesGroupList) - 1

            imagesGroupDict[imIdx] = lastGroup
        else:
            imagesGroupDict[imIdx] = 0

        fsf.Data.Sec.imagesGroupDict(subsection, imagesGroupDict)

        # ADD LINK TO THE ORIGINAL MATERIAL
        subsectionsList = fsf.Wr.SectionCurrent.getSubsectionsListForCurrTopSection()
        numNotesOnThePage = 0
        
        for subsec in subsectionsList:
            origMatNameDict = fsf.Data.Sec.origMatNameDict(subsec)
            
            for tempImIdx in list(fsf.Data.Sec.origMatNameDict(subsec).keys()):
                subsecPagesDict = fsf.Data.Sec.imLinkOMPageDict(subsec)

                if origMatNameDict[tempImIdx] == origMatName and subsecPagesDict[tempImIdx] == page:
                    numNotesOnThePage += 1

        numNotesOnThePage = str(numNotesOnThePage)
        
        currOMName = fsf.Data.Book.currOrigMatName
        bookName = sf.Wr.Manager.Book.getCurrBookName()
        currTopSection = fsf.Data.Book.currTopSection
        noteUrl = tff.Wr.TexFileUtils.getUrl(bookName, currTopSection, subsection, imIdx, "full")
        noteText = noteUrl + " " + imText
        fsf.Wr.OriginalMaterialStructure.addNoteToOriginalMaterial(currOMName, page, noteText, numNotesOnThePage)

        # Updating the remote
        msg = "Adding entry: " + subsection + "_" + imIdx
        ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)

        # POPULATE THE MAIN FILE
        tff.Wr.TexFilePopulate.populateCurrMainFile()

        dt.AppState.UseLatestGroup.setData(cls.appCurrDataAccessToken, False)

        return True

    @classmethod
    def AddLink(cls, wholeLinkPathStr, sourceSubsection, sourceIDX, sourceTopSection):
        import UI.widgets_facade as wf

        bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        bookName = sf.Wr.Manager.Book.getCurrBookName()

        wholeLinkPath = wholeLinkPathStr.split(".")
        
        if _u.Token.NotDef.str_t in wholeLinkPathStr:
            msg = "The path '{0}' is not correct. Please correct it.".format(wholeLinkPathStr)
            response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)

            mainManager = dt.AppState.UIManagers.getData(cls.appCurrDataAccessToken,
                                                        wf.Wr.MenuManagers.MathMenuManager)
            mainManager.show()

            return
        
        targetSubsection = ".".join(wholeLinkPath[:-1])
        targetTopSection = targetSubsection.split(".")[0]
        targetIDX = wholeLinkPath[-1]


        if sourceSubsection == targetSubsection:
            msg = "\
The source and target subsections  are the same and are '{0}'.\n\
This is not correct. Please correct it.".format(sourceSubsection)
            response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)

            mainManager = dt.AppState.UIManagers.getData(cls.appCurrDataAccessToken,
                                                        wf.Wr.MenuManagers.MathMenuManager)
            mainManager.show()

            return

        # add target to the source links
        sourseSectionGlobalLinksDict = fsf.Data.Sec.imGlobalLinksDict(sourceSubsection)
        
        if sourceIDX not in list(sourseSectionGlobalLinksDict.keys()):
            sourceImGlobalLinksDict = {}
        elif sourseSectionGlobalLinksDict[sourceIDX] == _u.Token.NotDef.dict_t:
            sourceImGlobalLinksDict = {}
        else:
            sourceImGlobalLinksDict = sourseSectionGlobalLinksDict[sourceIDX]
        
        targetUrl = tff.Wr.TexFileUtils.getUrl(bookName, targetTopSection, targetSubsection, 
                                                targetIDX, "full", False)
        targetUrlLinkName = targetSubsection + "_" + targetIDX

        # add target to the target info
        targetSectionGlobalLinksDict = fsf.Data.Sec.imGlobalLinksDict(targetSubsection)
        
        if targetIDX not in list(targetSectionGlobalLinksDict.keys()):
            targetImGlobalLinksDict = {}
        elif targetSectionGlobalLinksDict[targetIDX] == _u.Token.NotDef.dict_t:
            targetImGlobalLinksDict = {}
        else:
            targetImGlobalLinksDict = targetSectionGlobalLinksDict[targetIDX]

        sourceUrl = tff.Wr.TexFileUtils.getUrl(bookName, sourceTopSection, sourceSubsection, 
                                                sourceIDX, "full", False)
        sourceUrlLinkName = sourceSubsection + "_" + sourceIDX

        theLinksAreNotPresentMsg = []

        if targetUrlLinkName not in list(sourceImGlobalLinksDict.keys()) \
            and sourceUrlLinkName not in list(targetImGlobalLinksDict.keys()):
            msg = "Do you want to add link \
\nFrom: '{2}_{3}'\nTo: '{0}_{1}'?".format(targetSubsection, targetIDX, sourceSubsection, sourceIDX)
            response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)

            mainManager = dt.AppState.UIManagers.getData(cls.appCurrDataAccessToken,
                                                        wf.Wr.MenuManagers.MathMenuManager)
            mainManager.show()

            if not response:
                return

            # add link to the source
            sourceImGlobalLinksDict[targetUrlLinkName] = targetUrl

            if sourseSectionGlobalLinksDict == _u.Token.NotDef.dict_t:
                sourseSectionGlobalLinksDict = {}
            
            sourseSectionGlobalLinksDict[sourceIDX] = sourceImGlobalLinksDict
            fsf.Data.Sec.imGlobalLinksDict(sourceSubsection, sourseSectionGlobalLinksDict)

             # add link to the target
            targetImGlobalLinksDict[sourceUrlLinkName] = sourceUrl

            if targetSectionGlobalLinksDict == _u.Token.NotDef.dict_t:
                targetSectionGlobalLinksDict = {}

            targetSectionGlobalLinksDict[targetIDX] = targetImGlobalLinksDict
            fsf.Data.Sec.imGlobalLinksDict(targetSubsection, targetSectionGlobalLinksDict)

        elif targetUrlLinkName in list(sourceImGlobalLinksDict.keys()):
            m = "The source link: '{0}' is already present.\n".format(sourceUrl)
            theLinksAreNotPresentMsg.append(m)
            log.autolog(m)

        elif sourceUrlLinkName in list(targetImGlobalLinksDict.keys()): 
            m = "The target link: '{0}' is already present.".format(targetUrl)
            theLinksAreNotPresentMsg.append(m)
            log.autolog(m)
        
        if theLinksAreNotPresentMsg != []:
            response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification("".join(theLinksAreNotPresentMsg), True)

            mainManager = dt.AppState.UIManagers.getData(cls.appCurrDataAccessToken,
                                                        wf.Wr.MenuManagers.MathMenuManager)
            mainManager.show()

            return

        #
        # rebuild the pdfs
        #
        ocf.Wr.LatexCalls.buildPDF(bookPath, sourceSubsection, sourceIDX)
        ocf.Wr.LatexCalls.buildPDF(bookPath, targetSubsection, targetIDX)

        # Updating the remote
        msg = "Adding global link from: '{0}_{1}' to: '{2}_{3}'".format(sourceSubsection, sourceIDX,
                                                                        targetSubsection, targetIDX)
        ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)

    @classmethod
    def AddSubsection(cls, secPath, newSecName, newSecStartPage, newSecEndPage):
        import UI.widgets_facade as wf

        if not re.match("[[\d]+.]*\d+", secPath):
            msg = "\
The section with path :'{0}' has wrong format.\
Only '.' and '[0-9]' tokens are allowed. Can't create section.".format(secPath, newSecName, newSecStartPage, newSecEndPage)
            wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)

            mainManager = dt.AppState.UIManagers.getData(cls.appCurrDataAccessToken,
                                                        wf.Wr.MenuManagers.MathMenuManager)
            mainManager.show()
            return

        if secPath in fsf.Wr.BookInfoStructure.getSubsectionsList():
            msg = "\
The section with path :'{0}' already exists. Can't create section.".format(secPath, newSecName, newSecStartPage, newSecEndPage)
            wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)

            mainManager = dt.AppState.UIManagers.getData(cls.appCurrDataAccessToken,
                                                        wf.Wr.MenuManagers.MathMenuManager)
            mainManager.show()
            return
        
        msg = "\
Do you want to create subsection with path :'{0}', text '{1}', \
start page '{2}', end page '{3}'?".format(secPath, newSecName, newSecStartPage, newSecEndPage)
        response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)
        
        mainManager = dt.AppState.UIManagers.getData(cls.appCurrDataAccessToken,
                                                    wf.Wr.MenuManagers.MathMenuManager)
        mainManager.show()

        if response:
            # close current subsection FS window
            currSection = fsf.Data.Book.currSection
            lf.Wr.LayoutsManager.closeFSWindow(currSection)
            
            fsf.Wr.FileSystemManager.addSectionForCurrBook(secPath)

            separator = fsf.Data.Book.sections_path_separator

            topSectionName = secPath.split(separator)[0]
            fsf.Data.Book.currTopSection = topSectionName
            fsf.Data.Book.currSection = secPath
            sections = fsf.Data.Book.sections
            sections[topSectionName]["prevSubsectionPath"] = secPath
            fsf.Data.Book.sections = sections

            fsf.Data.Sec.text(secPath, newSecName)
            fsf.Data.Sec.start(secPath, newSecStartPage)
            fsf.Data.Sec.finish(secPath, newSecEndPage)

            # Updating the remote
            msg = "Adding the subsection: '{0}'".format(secPath)
            ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)

    def AddOM(origMatFilepath, origMatDestRelPath, origMatName):
        fsf.Wr.OriginalMaterialStructure.addOriginalMaterial(origMatFilepath,
                                                            origMatDestRelPath,
                                                            origMatName)

        # Updating the remote
        msg = "Adding the OM with name: '{0}'".format(origMatName)
        ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)
    

    def readdNotesToPage(currPage):
        omName = fsf.Data.Book.currOrigMatName
        fileName = fsf.Wr.OriginalMaterialStructure.getOriginalMaterialsFilename(omName)
        
        time.sleep(0.3)

        cmd = oscr.deleteAllNotesFromThePage(fileName, currPage)
        _u.runCmdAndWait(cmd)

        time.sleep(0.3)
        bookName = sf.Wr.Manager.Book.getCurrBookName()
        noteIdx = 1
        sections = fsf.Data.Book.sections
        for topSection in sections:
            subsections = fsf.Wr.BookInfoStructure.getSubsectionsList(topSection)
            for subSec in subsections:
                imPages:dict = fsf.Data.Sec.imLinkOMPageDict(subSec)
                imTexts:dict = fsf.Data.Sec.imLinkDict(subSec)
                for imIdx,imPage in imPages.items():
                    if imPage == currPage:
                        imText = imTexts[imIdx]
                        url = tff.Wr.TexFileUtils.getUrl(bookName, topSection, subSec, 
                                                        imIdx, "full", notLatex=True)
                        fsf.Wr.OriginalMaterialStructure.addNoteToOriginalMaterial(omName, currPage, 
                                                                                    url + " " + imText, noteIdx)
                        noteIdx += 1
