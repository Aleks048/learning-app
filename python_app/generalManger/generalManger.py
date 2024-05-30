import os
import sys
import re
import time
from AppKit import NSPasteboard, NSStringPboardType
from threading import Thread

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
import outside_calls.outside_calls_facade as oscf

import UI.widgets_facade as wf


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
        exMenuManager = wf.Wr.MenuManagers.ExcerciseManager()
        log.autolog("Started '{0}' UI manager".format("toc menu"))
        notesMenuManager = wf.Wr.MenuManagers.NotesManager()
        log.autolog("Started '{0}' UI manager".format("excercise menu"))
        proofsMenuManager = wf.Wr.MenuManagers.ProofsManager()
        log.autolog("Started '{0}' UI manager".format("proofs menu"))
        imagagesMenuManager = wf.Wr.MenuManagers.ImagesManager()
        log.autolog("Started '{0}' UI manager".format("image menu"))
        pdfReadersMenuManager = wf.Wr.MenuManagers.PdfReadersManager()
        log.autolog("Started '{0}' UI manager".format("pdfReader menu"))
        excerciseLineNoteManager = wf.Wr.MenuManagers.ExcerciseLineNoteManager()
        log.autolog("Started '{0}' UI manager".format("pdfReader menu"))

        log.autolog("-- Srartup  of other menus ended.")

        mainMenuManager.showOnly()
        mainMenuManager.moveTocToCurrEntry()


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
        
        # ex
        exManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                wf.Wr.MenuManagers.ExcerciseManager)
        exManager.winRoot.exitApp()

        # proof
        proofsManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                wf.Wr.MenuManagers.ProofsManager)
        proofsManager.winRoot.exitApp()

        # images
        imagesManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                wf.Wr.MenuManagers.ImagesManager)
        imagesManager.winRoot.exitApp()

        # pdfReader
        pdfReadersManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                wf.Wr.MenuManagers.PdfReadersManager)
        pdfReadersManager.updateOMpage()
        pdfReadersManager.winRoot.exitApp()

        # excerciseLineNoteManager
        excerciseLineNoteManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                wf.Wr.MenuManagers.ExcerciseLineNoteManager)
        excerciseLineNoteManager.winRoot.exitApp()

        # notes
        notesManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                wf.Wr.MenuManagers.NotesManager)
        notesManager.winRoot.exitApp()

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

        # Updating the remote
        msg = "Adding new book: " + bookName
        ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)

    
    def AddNewImageData(subsection, mainImIdx, imPath, eImIdx = None, textOnly = False):
        dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                wf.Wr.MenuManagers.PdfReadersManager).show(subsection = subsection,
                                                                            imIdx = mainImIdx,
                                                                            selector = True,
                                                                            extraImIdx = eImIdx,
                                                                            changePrevPos = True)            

        def __executeAfterImageCreated(subsection, mainImIdx, imPath, eImIdx, textOnly):
            timer = 0

            while not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(imPath):
                time.sleep(0.3)
                timer += 1

                if timer > 50:
                    break
            if eImIdx == None:
                imText = _u.getTextFromImage(imPath)

                if textOnly:
                    if imText == None:
                        imText = _u.Token.NotDef.str_t

                    imText = imText.replace("_", "\_")

                    imText = re.sub(r"([^\\]){", r"\1\\{", imText)
                    imText = re.sub(r"([^\\])}", r"\1\\}", imText)
                    imText = re.sub(r"([a-z]|[A-Z])\u0308", r"\\ddot{\1}", imText)
                    imText = re.sub(r"([a-z]|[A-Z])\u0300", r"\\grave{\1}", imText)
                    imText = re.sub(r"([a-z]|[A-Z])\u0301", r"\\acute{\1}", imText)

                    imText = imText.replace("[", "(")
                    imText = imText.replace("]", ")")
                    imText = imText.replace("\u201c", "\"")
                    imText = imText.replace("\u201d", "\"")
                    imText = imText.replace("\u2014", "-")
                    imText = imText.replace("\ufffd", "")
                    imText = imText.replace("\n", "")
                    imText = imText.replace("\u0000", "fi")
                    imText = imText.replace("\u0394", "\\Delta ")

                imageTextsDict = fsf.Data.Sec.imageText(subsection)
                imageTextsDict = {} if imageTextsDict == _u.Token.NotDef.dict_t else imageTextsDict
                imageTextsDict[mainImIdx] = imText
                fsf.Data.Sec.imageText(subsection, imageTextsDict)
            else:
                eImText = _u.getTextFromImage(imPath)
                eImageTextsDict = fsf.Data.Sec.extraImText(subsection)
                eImageTextsDict = {} if eImageTextsDict == _u.Token.NotDef.dict_t else eImageTextsDict

                if mainImIdx not in list(eImageTextsDict.keys()):
                    eImageTextsList = []
                else:
                    eImageTextsList = eImageTextsDict[mainImIdx]

                if int(eImIdx) == len(eImageTextsList):
                    eImageTextsList.append(eImText)
                else:
                    eImageTextsList[int(eImIdx)] = eImText

                eImageTextsDict[mainImIdx] = eImageTextsList
                fsf.Data.Sec.extraImText(subsection, eImageTextsDict)

        t = Thread(target = __executeAfterImageCreated, args = [subsection, mainImIdx, imPath, eImIdx, textOnly])
        t.start()
    @classmethod
    def AddExtraImageForEntry(cls, mainImIdx, subsection, extraImageIdx, extraImText):
        # update the content file
        extraImagesDict = fsf.Data.Sec.extraImagesDict(subsection)

        extraImagesList = []

        if extraImagesDict == _u.Token.NotDef.dict_t:
            extraImagesDict = {}

        if mainImIdx in list(extraImagesDict.keys()):
            extraImagesList = extraImagesDict[mainImIdx]

        extraImagesList.append(extraImText)

        if extraImageIdx == _u.Token.NotDef.str_t:
            extraImageIdx = len(extraImagesList) - 1

        currBokkPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        extraImagePath_curr = _upan.Paths.Screenshot.getAbs(currBokkPath, subsection)

        extraImageName = _upan.Names.getExtraImageFilename(mainImIdx, subsection, extraImageIdx)
        extraImagePathFull = os.path.join(extraImagePath_curr, extraImageName + ".png")

        cls.AddNewImageData(subsection, mainImIdx, extraImagePathFull, extraImageIdx)


        extraImagesDict[mainImIdx] = extraImagesList
        fsf.Data.Sec.extraImagesDict(subsection, extraImagesDict)

        if "proof" in extraImText.lower():
            dt.AppState.ShowProofs.setData(cls.appCurrDataAccessToken,
                                           True) 

    @classmethod
    def AddEntry(cls, subsection, imIdx:str, imText:str, 
                 addToTOCwIm:bool, textOnly:bool = False):
        import UI.widgets_facade as wf

        currBorrPath = sf.Wr.Manager.Book.getCurrBookFolderPath()

        imagePath = _upan.Paths.Screenshot.Images.getMainEntryImageAbs(currBorrPath,
                                                                       subsection,
                                                                       str(imIdx))

        # take a screenshot
        if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(imagePath):
            msg = "The image with idx '{0}' already exists.\n Overrite?".format(imIdx)
            response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)
            
            if response:
                ocf.Wr.FsAppCalls.deleteFile(imagePath)

                dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                    wf.Wr.MenuManagers.PdfReadersManager).show(subsection = subsection,
                                                                                imIdx = imIdx,
                                                                                selector = True,
                                                                                removePrevLabel = True)

                cls.AddNewImageData(subsection, imIdx, imagePath)

            mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken", 
                                                wf.Wr.MenuManagers.MathMenuManager)

            mainManager.show()

            if not response:
                return
        else:
            cls.AddNewImageData(subsection, imIdx, imagePath)

        def __afterImageCreated(cls, subsection, imIdx:str, imText:str, 
                                 addToTOCwIm:bool, textOnly:bool = False):
            currBorrPath = sf.Wr.Manager.Book.getCurrBookFolderPath()

            imagePath = _upan.Paths.Screenshot.Images.getMainEntryImageAbs(currBorrPath,
                                                                        subsection,
                                                                        str(imIdx))

            timer = 1

            while not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(imagePath):
                time.sleep(0.3)
                timer += 1

                if timer > 50:
                    return False

            textOnlyDict = fsf.Data.Sec.textOnly(subsection)
            textOnlyDict[imIdx] = textOnly
            fsf.Data.Sec.textOnly(subsection, textOnlyDict)

            # STOTE IMNUM, IMNAME AND LINK
            if imText == _u.Token.NotDef.str_t:
                while fsf.Data.Sec.imageText(subsection).get(imIdx) == None:
                    while str(fsf.Data.Sec.imageText(subsection).get(imIdx)) == _u.Token.NotDef.str_t:
                        time.sleep(0.1)
                imText = fsf.Data.Sec.imageText(subsection)[imIdx]

            fsf.Wr.SectionCurrent.setImLinkAndIDX(imText, imIdx)

            # ORIGINAL MATERIAL DATA
            origMatName = fsf.Data.Book.currOrigMatName

            pdfReadersManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                wf.Wr.MenuManagers.PdfReadersManager)
            pdfReadersManager.updateOMpage()

            try:
                page = str(fsf.Data.Sec.figuresLabelsData(subsection)[imIdx]["page"])
            except:
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
            # tff.Wr.TexFilePopulate.populateCurrMainFile()

            dt.AppState.UseLatestGroup.setData(cls.appCurrDataAccessToken, False)

        t = Thread(target = __afterImageCreated, args = [cls, subsection, imIdx, imText,\
                                                          addToTOCwIm, textOnly])
        t.start()

        return True


    @classmethod
    def RemoveGlLink(cls, targetSubsection, sourceSubsection, sourceIDX, targetIDX):
        # add target to the source links
        sourseSectionGlobalLinksDict = fsf.Data.Sec.imGlobalLinksDict(sourceSubsection)
        sourceLinks = sourseSectionGlobalLinksDict[sourceIDX]
        sourceLinks.pop(f"{targetSubsection}_{targetIDX}")
        
        if sourceLinks == {}:
            sourseSectionGlobalLinksDict.pop(sourceIDX)

        fsf.Data.Sec.imGlobalLinksDict(sourceSubsection, sourseSectionGlobalLinksDict)        

        targetSectionGlobalLinksDict = fsf.Data.Sec.imGlobalLinksDict(targetSubsection)
        targetLinks = targetSectionGlobalLinksDict[targetIDX]
        targetLinks.pop(f"{sourceSubsection}_{sourceIDX}")

        if targetLinks == {}:
            targetSectionGlobalLinksDict.pop(targetIDX)

        fsf.Data.Sec.imGlobalLinksDict(targetSubsection, targetSectionGlobalLinksDict)        

    @classmethod
    def CopyGlLink(cls, targetSubsection, targetIDX, sourceSubsection, sourceIDX):
         # add target to the source links
        sourseSectionGlobalLinksDict = fsf.Data.Sec.imGlobalLinksDict(sourceSubsection)
        sourceLinks = sourseSectionGlobalLinksDict[sourceIDX].copy()
        targetTopSection = targetSubsection.split(".")[0]

        for sl, slfull in sourceLinks.items():
            if "KIK:" in slfull:
                slsubsection = sl.split("_")[0]
                slImIdx = sl.split("_")[1]
                cls.AddLink(slsubsection + "." + slImIdx, 
                            targetSubsection, targetIDX, targetTopSection, False)
            else:
                cls.AddWebLink(sl, slfull, targetSubsection, targetIDX, targetTopSection, False)

    @classmethod
    def RetargetGlLink(cls, targetSubsection, targetIDX, sourceSubsection, sourceIDX):
         # add target to the source links
        sourseSectionGlobalLinksDict = fsf.Data.Sec.imGlobalLinksDict(sourceSubsection)

        if sourseSectionGlobalLinksDict[sourceIDX] == _u.Token.NotDef.str_t:
            return

        sourceLinks = sourseSectionGlobalLinksDict[sourceIDX].copy()

        for sl, slfull in sourceLinks.items():
            if "KIK:" in slfull:
                slsubsection = sl.split("_")[0]
                slImIdx = sl.split("_")[1]
                cls.RemoveGlLink(slsubsection, sourceSubsection, sourceIDX, slImIdx)
            else:
                cls.RemoveWebLink(sourceSubsection, sourceIDX, sl)

        targetTopSection = targetSubsection.split(".")[0]

        for sl, slfull in sourceLinks.items():
            if "KIK:" in slfull:
                slsubsection = sl.split("_")[0]
                slImIdx = sl.split("_")[1]
                cls.AddLink(slsubsection + "." + slImIdx, 
                            targetSubsection, targetIDX, targetTopSection, False)
            else:
                cls.AddWebLink(sl, slfull, targetSubsection, targetIDX, targetTopSection, False)

    @classmethod
    def RemoveWebLink(cls, sourceSubsection, sourceIDX, webLinkName):
        # add target to the source links
        sourseSectionGlobalLinksDict = fsf.Data.Sec.imGlobalLinksDict(sourceSubsection)
        sourceLinks = sourseSectionGlobalLinksDict[sourceIDX]
        sourceLinks.pop(f"{webLinkName}")
        
        if sourceLinks == {}:
            sourseSectionGlobalLinksDict.pop(sourceIDX)

            if sourseSectionGlobalLinksDict == {}:
                sourseSectionGlobalLinksDict = _u.Token.NotDef.dict_t.copy()

        fsf.Data.Sec.imGlobalLinksDict(sourceSubsection, sourseSectionGlobalLinksDict)

    @classmethod
    def AddLink(cls, wholeLinkPathStr, sourceSubsection, sourceIDX, sourceTopSection, shouldConfirm = True):
        import UI.widgets_facade as wf

        bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        bookName = sf.Wr.Manager.Book.getCurrBookName()

        wholeLinkPath = wholeLinkPathStr.split(".")
        
        if _u.Token.NotDef.str_t in wholeLinkPathStr:
            msg = "The path \n\n'{0}'\n\n is not correct.\n Please correct it.".format(wholeLinkPathStr)
            response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)

            mainManager = dt.AppState.UIManagers.getData(cls.appCurrDataAccessToken,
                                                        wf.Wr.MenuManagers.MathMenuManager)
            mainManager.show()

            return
        
        targetSubsection = ".".join(wholeLinkPath[:-1])
        targetTopSection = targetSubsection.split(".")[0]
        targetIDX = wholeLinkPath[-1]

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

            if shouldConfirm:
                msg = "\
Do you want to add link \n\nFrom: '{0}_{1}', \nwith text:\n '{4}'\n\n\nTo: '{2}_{3}', \nwith text:\n '{5}'?"\
                    .format(targetSubsection, 
                            targetIDX, 
                            sourceSubsection, 
                            sourceIDX,
                            fsf.Data.Sec.imLinkDict(targetSubsection)[targetIDX],
                            fsf.Data.Sec.imLinkDict(sourceSubsection)[sourceIDX]
                            )
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
            targetSectionGlobalLinksDict = fsf.Data.Sec.imGlobalLinksDict(targetSubsection)

            if targetIDX not in list(targetSectionGlobalLinksDict.keys()):
                targetImGlobalLinksDict = {}
            elif targetSectionGlobalLinksDict[targetIDX] == _u.Token.NotDef.dict_t:
                targetImGlobalLinksDict = {}
            else:
                targetImGlobalLinksDict = targetSectionGlobalLinksDict[targetIDX]

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
            m = "The target link: \n\n'{0}'\n\n is already present.".format(targetUrl)
            theLinksAreNotPresentMsg.append(m)
            log.autolog(m)
        
        if (theLinksAreNotPresentMsg != []) and shouldConfirm:
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
    def AddWebLink(cls, linkeName, wholeLinkPathStr, 
                   sourceSubsection, sourceIDX, sourceTopSection,
                   shouldConfirm = True):
        import UI.widgets_facade as wf

        bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        bookName = sf.Wr.Manager.Book.getCurrBookName()

        # add target to the source links
        sourseSectionGlobalLinksDict = fsf.Data.Sec.imGlobalLinksDict(sourceSubsection)

        if sourceIDX not in list(sourseSectionGlobalLinksDict.keys()):
            sourceImGlobalLinksDict = {}
        elif sourseSectionGlobalLinksDict[sourceIDX] == _u.Token.NotDef.dict_t:
            sourceImGlobalLinksDict = {}
        else:
            sourceImGlobalLinksDict = sourseSectionGlobalLinksDict[sourceIDX]

        sourceUrl = tff.Wr.TexFileUtils.getUrl(bookName, sourceTopSection, sourceSubsection, 
                                                sourceIDX, "full", False)

        theLinksAreNotPresentMsg = []

        if linkeName not in list(sourceImGlobalLinksDict.keys()):
            if shouldConfirm:
                msg = "Do you want to add WEB link From: \n\n'{1}_{2}'.\n\nWith name: \n'{3}'\n\nWith address: \n'{0}'?"\
                        .format(wholeLinkPathStr, 
                                sourceSubsection, 
                                sourceIDX,
                                linkeName)
                response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)

                mainManager = dt.AppState.UIManagers.getData(cls.appCurrDataAccessToken,
                                                            wf.Wr.MenuManagers.MathMenuManager)
                mainManager.show()

                if not response:
                    return

            # add link to the source
            sourceImGlobalLinksDict[linkeName] = wholeLinkPathStr

            if sourseSectionGlobalLinksDict == _u.Token.NotDef.dict_t:
                sourseSectionGlobalLinksDict = {}

            sourseSectionGlobalLinksDict[sourceIDX] = sourceImGlobalLinksDict
            fsf.Data.Sec.imGlobalLinksDict(sourceSubsection, sourseSectionGlobalLinksDict)
        else:
            m = "The SOURCE link: \n\n'{0}'\n\n is already present.\n".format(sourceUrl)
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

        # Updating the remote
        msg = "Adding web link: '{0}' from: '{1}_{2}'".format(wholeLinkPathStr, sourceSubsection, sourceIDX)
        ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)

    @classmethod
    def AddSubsection(cls, secPath, newSecName, newSecStartPage, newSecEndPage, shouldAsk = True):
        import UI.widgets_facade as wf

#         if not re.match("[[\d]+.]*\d+", secPath):
#             msg = "\
# The section with path :\n'{0}'\n has wrong format.\n\n\
# Only '.' and '[0-9]' tokens are allowed. Can't create section.".format(secPath)
#             wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)

#             mainManager = dt.AppState.UIManagers.getData(cls.appCurrDataAccessToken,
#                                                         wf.Wr.MenuManagers.MathMenuManager)
#             mainManager.show()
#             return

        if secPath in fsf.Wr.BookInfoStructure.getSubsectionsList():
            msg = "\
The section with path :\n'{0}'\n already exists. \n\n\
Can't create section.".format(secPath, newSecName, newSecStartPage, newSecEndPage)
            wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)

            mainManager = dt.AppState.UIManagers.getData(cls.appCurrDataAccessToken,
                                                        wf.Wr.MenuManagers.MathMenuManager)
            mainManager.show()
            return
        
        if shouldAsk:
            msg = "\
    Do you want to create subsection \n\n\
    with path :\n'{0}', \n\n\
    text \n'{1}', \n\n\
    start page '{2}', end page '{3}'?".format(secPath, newSecName, newSecStartPage, newSecEndPage)
            response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)
            
            mainManager = dt.AppState.UIManagers.getData(cls.appCurrDataAccessToken,
                                                        wf.Wr.MenuManagers.MathMenuManager)
            mainManager.show()
        else:
            response = True

        if response:
            if "." in secPath:
                # close current subsection FS window
                currSection = fsf.Data.Book.currSection
                # lf.Wr.LayoutsManager.closeFSWindow(currSection)
                
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
            else:
                fsf.Wr.FileSystemManager.addTopSectionForCurrBook(secPath)
                sections  = fsf.Data.Book.sections
                section = sections[secPath]
                section["name"] = newSecName
                fsf.Data.Book.sections = sections


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

    def deleteSubsection(sourceSubsection):            
        # Updating the remote
        msg = f"Before the subsection '{sourceSubsection}'."
        ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)

        fsf.Wr.SectionInfoStructure.removeSection(sourceSubsection)
        fsf.Wr.BookInfoStructure.removeSection(sourceSubsection)

        msg = f"After the subsection '{sourceSubsection}'."
        ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)

    @classmethod
    def moveSubsection(cls, sourceSubsection, targetSubsection):
        # Updating the remote
        msg = f"Before Moving the subsection '{sourceSubsection}' to '{targetSubsection}'."
        ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)

        currBookpath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        
        if (targetSubsection in sourceSubsection) or \
            (sourceSubsection in targetSubsection):
            tempSubsection = sourceSubsection.split(".")[0] + ".10000"

            fsf.Wr.SectionInfoStructure.moveSection(currBookpath,
                                                    sourceSubsection, 
                                                    tempSubsection,
                                                    shouldRebuild = False)

            fsf.Wr.BookInfoStructure.moveSection(sourceSubsection, tempSubsection)

            if targetSubsection in sourceSubsection:
                cls.deleteSubsection(targetSubsection)

            fsf.Wr.SectionInfoStructure.moveSection(currBookpath,
                                                    tempSubsection, 
                                                    targetSubsection)

            fsf.Wr.BookInfoStructure.moveSection(tempSubsection, targetSubsection)
        else:
            fsf.Wr.SectionInfoStructure.moveSection(currBookpath,
                                                    sourceSubsection, 
                                                    targetSubsection)

            fsf.Wr.BookInfoStructure.moveSection(sourceSubsection, targetSubsection)
        
        # Updating the remote
        msg = f"After Moving the subsection '{sourceSubsection}' to '{targetSubsection}'."
        ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)

    @classmethod
    def moveGroupToSubsection(cls, 
                              sourceSubsection, sourceGroupName, 
                              targetSubsection, targetGroupName, targetEntryDestIdx):
        sourceGroupIdx = list(fsf.Data.Sec.imagesGroupsList(sourceSubsection).keys()).index(sourceGroupName)
        firstGroupEntry = list({k:v for k,v in fsf.Data.Sec.imagesGroupDict(sourceSubsection).items() \
                            if v == sourceGroupIdx}.keys())[0]
        startPage = fsf.Data.Sec.imLinkOMPageDict(sourceSubsection)[firstGroupEntry]

        # check if targetSubsection exists
        if targetSubsection not in fsf.Wr.BookInfoStructure.getSubsectionsList():
            cls.AddSubsection(targetSubsection, 
                              sourceGroupName, 
                              startPage,
                              _u.Token.NotDef.str_t,
                              shouldAsk = False)
        
        targetImagesGroupsList = fsf.Data.Sec.imagesGroupsList(targetSubsection)
    
        #  check if we need to add the group
        if targetGroupName not in targetImagesGroupsList:
            targetImagesGroupsList[targetGroupName] = True
            fsf.Data.Sec.imagesGroupsList(targetSubsection, targetImagesGroupsList)

        # move all the entries of the group to target subsection group
        sourceImagesGroupDict:dict = fsf.Data.Sec.imagesGroupDict(sourceSubsection)
        sourceImagesGroupDict = {k:v for k,v in sourceImagesGroupDict.items() if v == sourceGroupIdx}
        targetImagesGroupidx = len(list(fsf.Data.Sec.imagesGroupsList(targetSubsection).keys())) - 1

        while sourceImagesGroupDict != {}:
            currEntryIdx = list(sourceImagesGroupDict.keys())[0]
            fsf.Wr.SectionInfoStructure.insertEntryAfterIdx(sourceSubsection, currEntryIdx,
                                                            targetSubsection, targetEntryDestIdx,
                                                            cutEntry = True, shouldAsk = False)

            targetImagesGroupDict = fsf.Data.Sec.imagesGroupDict(targetSubsection)
            targetImagesGroupDict[targetEntryDestIdx] = targetImagesGroupidx
            fsf.Data.Sec.imagesGroupDict(targetSubsection, targetImagesGroupDict)

            targetEntryDestIdx = str(int(targetEntryDestIdx) + 1)
            sourceImagesGroupDict = fsf.Data.Sec.imagesGroupDict(sourceSubsection)
            sourceImagesGroupDict = {k:v for k,v in sourceImagesGroupDict.items() if v == sourceGroupIdx}
        
        # when there are no entries in the group delete the group and adjust the other images groups accordingly
        sourceImagesGroupDict = fsf.Data.Sec.imagesGroupDict(sourceSubsection)

        sourceImagesGroupsList:dict = fsf.Data.Sec.imagesGroupsList(sourceSubsection)
        sourceImagesGroupsList.pop(sourceGroupName)
        fsf.Data.Sec.imagesGroupsList(sourceSubsection, sourceImagesGroupsList)
        gi = str(sourceGroupIdx)
        groupImgPath = _upan.Paths.Screenshot.Images.getGroupImageAbs(sf.Wr.Manager.Book.getCurrBookName(), 
                                                                              sourceSubsection,
                                                                              gi)
        oscf.Wr.FsAppCalls.deleteFile(groupImgPath)
        
        for k,v in sourceImagesGroupDict.items():
            if int(v) > int(sourceGroupIdx):
                sourceImagesGroupDict[k] = v - 1

        for k in sourceImagesGroupsList.keys():
            fsf.Wr.SectionInfoStructure.rebuildGroupOnlyImOnlyLatex(sourceSubsection, k)
        
        fsf.Data.Sec.imagesGroupDict(sourceSubsection, sourceImagesGroupDict)

        fsf.Wr.SectionInfoStructure.rebuildEntriesBatch(sourceSubsection, "0")
        fsf.Wr.SectionInfoStructure.rebuildEntriesBatch(targetSubsection, "0")

    def readdNotesToPage(currPage):
        return
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
