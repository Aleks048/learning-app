import time

import _utils.logging as log

import file_system.file_system_facade as fsf

import layouts.layouts_facade as lm

import data.temp as dt

import UI.widgets_facade as wf

import outside_calls.outside_calls_facade as oscf

import _utils._utils_main as _u
import _utils.pathsAndNames as _upan



def processCall(url):
    log.autolog("Processing url request: '{0}'.".format(url))
    url = url.replace("KIK:/", "")
    url = url.split("/")
    bookName = url[0]
    topSection = url[1]
    subsecPath = url[2]
    positionIDX = url[3]

    if len(url) > 4:
        linktType:str = url[4]

    if "notes" in linktType.lower():
        notesAppLink = fsf.Data.Sec.notesAppLink(subsecPath)
        if notesAppLink != _u.Token.NotDef.str_t:
            log.autolog("Will only open notesapp page of '{0}'".format(subsecPath))
            oscf.Wr.NoteAppCalls.openPage(notesAppLink)
        else:
            log.autolog("Notesapp link of '{0}' is empty. Cannot open it".format(subsecPath))
        return

    if positionIDX == _u.Token.NotDef.str_t:
        positionIDX = fsf.Wr.Links.ImIDX.get(subsecPath)
    
    if "pdf" in linktType.lower():
        log.autolog("Will only open pdf of '{0}'".format(subsecPath))
        oscf.Wr.PdfApp.openSubsectionPDF(positionIDX,
                                        subsecPath,
                                        bookName)
        return    

    fileNum = _upan.Paths.TexFiles.getEnding(subsecPath, positionIDX)
    # switch section
    if not (subsecPath == fsf.Data.Book.currSection \
        and fileNum == str(lm.Wr.SectionLayout.currFileNum)):
        lm.Wr.SectionLayout.close()
        time.sleep(0.3)

        fsf.Data.Book.currSection = subsecPath
        fsf.Data.Book.currTopSection = topSection

        # UI
        mainMenuManager = dt.AppState.UIManagers.getData("fake data access token", 
                                                        wf.Wr.MenuManagers.MainMenuManager.__base__)
        mainMenuManager.switchToSectionLayout()
    
    # other sections UI
    lm.Wr.SectionLayout.set(imIdx=positionIDX)
