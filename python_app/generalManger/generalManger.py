import os
import sys
import re
import time
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

import outside_calls.outside_calls_facade as oscf

import UI.widgets_facade as wf

class GeneralManger(dc.AppCurrDataAccessToken):
    daemonThread = None
    dserver = None

    @classmethod
    def StartNonStartMenus(cls):
        # start the daemon to process client calls
        cls.daemonThread, cls.dserver = ds.startMainServerDaemon()

        wf.Wr.UI_generalManager.startNonStartMenus()


    @classmethod
    def StartApp(cls):
        wf.Wr.UI_generalManager.startup()
        

    @classmethod
    def ExitApp(cls):
        wf.Wr.UI_generalManager.exit()

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

    
    def __AddNewImageData(subsection, mainImIdx, imPath, eImIdx = None, textOnly = False):
        wf.Wr.UI_generalManager.addImage(subsection = subsection,
                               imIdx = mainImIdx,
                               extraImIdx = eImIdx,
                               selector = True,
                               changePrevPos = True,
                               withoutRender = True)        

        fsf.Wr.SectionInfoStructure.addNewImage(subsection, mainImIdx, imPath, eImIdx, textOnly)


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

        cls.__AddNewImageData(subsection, mainImIdx, extraImagePathFull, extraImageIdx)


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
        if not fsf.Data.Sec.isVideo(subsection):
            if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(imagePath):
                msg = "The image with idx '{0}' already exists.\n Overrite?".format(imIdx)
                response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)
                
                if response:
                    ocf.Wr.FsAppCalls.deleteFile(imagePath)

                    cls.__AddNewImageData(subsection, imIdx, imagePath)

                if not response:
                    return
            else:
                cls.__AddNewImageData(subsection, imIdx, imagePath)

        def __afterImageCreated(cls, subsection, imIdx:str, imText:str, 
                                 addToTOCwIm:bool, textOnly:bool = False):
            currBorrPath = sf.Wr.Manager.Book.getCurrBookFolderPath()

            isVideo = fsf.Data.Sec.isVideo(subsection)

            if not isVideo:
                imagePath = _upan.Paths.Screenshot.Images.getMainEntryImageAbs(currBorrPath,
                                                                            subsection,
                                                                            str(imIdx))

                timer = 1

                while not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(imagePath):
                    time.sleep(0.3)
                    timer += 1

                    if timer > 50:
                        return False
            else:
                textOnly = True
            

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
            if not isVideo:
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
            else:
                #Get the position of the video
                pdfReadersManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.PdfReadersManager)
                videoPositionDict = fsf.Data.Sec.videoPosition(subsection)
                videoPositionDict[imIdx] = pdfReadersManager.getVideoPosition()
                fsf.Data.Sec.videoPosition(subsection, videoPositionDict)

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
            if not isVideo:
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

            if fsf.Data.Sec.isVideo(subsection):
                pdfReadersManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                                        wf.Wr.MenuManagers.PdfReadersManager)
                pdfReadersManager.showVideo(subsection, imIdx)

        t = Thread(target = __afterImageCreated, args = [cls, subsection, imIdx, imText,\
                                                          addToTOCwIm, textOnly])
        t.start()

        return True


    @classmethod
    def RemoveGlLink(cls, targetSubsection, sourceSubsection, sourceIDX, targetIDX):
        if sourceSubsection == targetSubsection:
            if int(sourceIDX) < int(targetIDX):
                temp = sourceIDX
                sourceIDX = targetIDX
                targetIDX = temp
        
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
    def AddSubsection(cls, secPath, newSecName, newSecStartPage, newSecEndPage, isVideo = False, shouldAsk = True):
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
                fsf.Data.Sec.isVideo(secPath, isVideo)
            else:
                fsf.Wr.FileSystemManager.addTopSectionForCurrBook(secPath)
                sections  = fsf.Data.Book.sections
                section = sections[secPath]
                section["name"] = newSecName
                fsf.Data.Book.sections = sections


            # Updating the remote
            msg = "Adding the subsection: '{0}'".format(secPath)
            ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)


    def DeleteSubsection(sourceSubsection):            
        # Updating the remote
        msg = f"Before the subsection '{sourceSubsection}'."
        ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)

        fsf.Wr.SectionInfoStructure.removeSection(sourceSubsection)
        fsf.Wr.BookInfoStructure.removeSection(sourceSubsection)

        msg = f"After the subsection '{sourceSubsection}'."
        ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)


    @classmethod
    def MoveSubsection(cls, sourceSubsection, targetSubsection):
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
                cls.DeleteSubsection(targetSubsection)

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
    def MoveGroupToSubsection(cls, sourceSubsection, sourceGroupName, 
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
                              fsf.Data.Sec.isVideo(targetSubsection),
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
                                                            cutEntry = True)

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
    
    @classmethod
    def AddAddMarkerToCode(cls, subsection, imIdx, 
                                vsCodeFilePath, subsectionCodeprojectPath, 
                                shouldDelete, bookcCodeMarker):
        relFilepath = ""

        if bookcCodeMarker:
            # ask the user if we wnat to proceed.
            if not shouldDelete:
                msg = "Do you want to add marker for book code project \n\n'{0}_{1}'?".format(subsection, imIdx)
            else:
                msg = "Do you want to delete marker for book code project \n\n'{0}_{1}'?".format(subsection, imIdx)
            
            response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)

            mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.MathMenuManager)
            mainManager.show()
            mainManager.moveTocToEntry(subsection, imIdx.split("_")[0])

            if not response:
                return

            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()

            bookCodeFilesRoot = _upan.Paths.Book.Code.getAbs(bookPath)

            relFilepath = vsCodeFilePath.replace(bookCodeFilesRoot + "/", "")

            log.autolog(f"\
        Add marker to VsCode for book project for file '{relFilepath}'\n\
        for '{subsection}':'{imIdx}'")

            bookCodeFile:dict = fsf.Data.Sec.bookCodeFile(fsf.Data.Book.currSection)

            if not shouldDelete:
                if bookCodeFile.get(imIdx) == None:
                    bookCodeFile[imIdx] = relFilepath
                    fsf.Data.Sec.bookCodeFile(fsf.Data.Book.currSection, bookCodeFile)

                    return _upan.Names.codeLineMarkerBook(subsection, imIdx)
                else:
                    return "CODE_MARKER: marker is already present. Please remove before adding."
            else:
                if bookCodeFile.get(imIdx) == None:
                    _u.log.autolog("Deleting the marker for book code project for {subsection}_{imIdx}.\n Marker not present.")
                    return "CODE_MARKER: delete marker is not present. "
                else:
                    _u.log.autolog("Deleting the marker for book code project for {subsection}_{imIdx}")
                    bookCodeFile.pop(imIdx)
                    fsf.Data.Sec.bookCodeFile(fsf.Data.Book.currSection, bookCodeFile)

                    return _upan.Names.codeLineMarkerBook(subsection, imIdx)

        else:
            # subsectionmarker
            # 
            # ask the user if we wnat to proceed.
            if not shouldDelete:
                msg = "Do you want to add marker for subsection code project \n\n'{0}_{1}'?".format(subsection, imIdx)
            else:
                msg = "Do you want to delete marker for subsection code project \n\n'{0}_{1}'?".format(subsection, imIdx)

            response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)

            mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.MathMenuManager)
            mainManager.show()
            mainManager.moveTocToEntry(subsection, imIdx.split("_")[0])

            if not response:
                return

            relFilepath = vsCodeFilePath.replace(subsectionCodeprojectPath + "/", "")

            log.autolog(f"\
        Add marker to VsCode for subsection project for file '{relFilepath}'\n\
        for '{subsection}':'{imIdx}'")
            subsectionCodeFile:dict = fsf.Data.Sec.subsectionCodeFile(fsf.Data.Book.currSection)

            if not shouldDelete:
                if subsectionCodeFile.get(imIdx) == None:
                    subsectionCodeFile[imIdx] = relFilepath
                    fsf.Data.Sec.subsectionCodeFile(fsf.Data.Book.currSection, subsectionCodeFile)

                    return _upan.Names.codeLineMarkerSubsection(subsection, imIdx)
                else:
                    return "CODE_MARKER: marker is already present. Please remove before adding" 
            else:
                if subsectionCodeFile.get(imIdx) == None:
                    _u.log.autolog("Deleting the marker for subsection code project for {subsection}_{imIdx}.\n Marker not present.")
                    return "CODE_MARKER: delete marker is not present."
                else:
                    _u.log.autolog("Deleting the marker for subsection code roject for {subsection}_{imIdx}")
                    subsectionCodeFile.pop(imIdx)
                    fsf.Data.Sec.subsectionCodeFile(fsf.Data.Book.currSection, subsectionCodeFile)

                    return _upan.Names.codeLineMarkerSubsection(subsection, imIdx)
