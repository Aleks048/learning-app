import time
import os

import _utils.logging as log

import file_system.file_system_facade as fsf

import data.temp as dt

import UI.widgets_facade as wf

import outside_calls.outside_calls_facade as oscf

import _utils._utils_main as _u
import _utils.pathsAndNames as _upan

import settings.facade as sf
import scripts.osascripts as oscr


def processCall(url):
    log.autolog("Processing url request: '{0}'.".format(url))

    if "KIK://" in url:
        url = url.replace("KIK://", "")
    else:
        url = url.replace("KIK:/", "")
    url = url.split("/")
    bookName = url[0]
    topSection = url[1]
    subsecPath = url[2]
    positionIDX = url[3]

    if len(url) > 4:
        linktType:str = url[4]

    if "om" in linktType.lower():
        pagesDict:dict = fsf.Data.Sec.imLinkOMPageDict(subsecPath)
        
        if positionIDX not in pagesDict.keys():
            log.autolog("Can't open original material for '{0}'.".format("/".join(url)))

        omNameDict = fsf.Data.Sec.origMatNameDict(subsecPath)
        omName = omNameDict[positionIDX]

        omPath = fsf.Wr.OriginalMaterialStructure.getMaterialPath(omName)
        page = pagesDict[positionIDX]
        
        oscf.Wr.PdfApp.openPDF(omPath, page)

        zoomLevel = fsf.Wr.OriginalMaterialStructure.getMaterialZoomLevel(omName)
        pdfToken:str = omPath.split("/")[-1].replace(".pdf", "")
        cmd = oscr.setDocumentScale(pdfToken, zoomLevel)
        _u.runCmdAndWait(cmd)

        return

    if positionIDX == _u.Token.NotDef.str_t:
        positionIDX = fsf.Wr.Links.ImIDX.get(subsecPath)
    
    if "pdf" in linktType.lower():
        log.autolog("Will only open pdf of '{0}'".format(subsecPath))
        oscf.Wr.PdfApp.openSubsectionPDF(positionIDX,
                                        subsecPath,
                                        bookName)
        return    

    # switch section
    if not (subsecPath == fsf.Data.Book.currSection):
        time.sleep(0.3)

        fsf.Data.Book.currSection = subsecPath
        fsf.Data.Book.currTopSection = topSection

        # UI
        mainMenuManager = dt.AppState.UIManagers.getData("fake data access token", 
                                                        wf.Wr.MenuManagers.MathMenuManager.__base__)
        mainMenuManager.switchToSectionLayout()
