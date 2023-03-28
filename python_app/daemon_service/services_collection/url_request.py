import outside_calls.outside_calls_facade as ocf

import _utils.logging as log

import file_system.file_system_facade as fsf

import layouts.layouts_facade as lm

import data.constants as dc
import data.temp as dt

import UI.widgets_facade as wf

import scripts.osascripts as oscr
import outside_calls.outside_calls_facade as oscf



def processCall(url):
    log.autolog("Processing url request: '{0}'.".format(url))
    url = url.replace("KIK:/", "")
    url = url.split(".")
    bookName = url[0]
    topSection = url[1]
    subsecPath = url[2]
    positionIDX = url[3]
    
    newSubsection = topSection + "." + subsecPath
    
    if len(url) > 4:
        linktType = url[4]
    
    if linktType == "pdf":
        log.autolog("Will only open pdf of '{0}'".format(newSubsection))
        oscf.Wr.PdfApp.openSubsectionPDF(positionIDX, 
                                        topSection,
                                        subsecPath,
                                        bookName)    
        return    

    # switch section
    
    if newSubsection != fsf.Data.Book.currSection:
        lm.Wr.SectionLayout.close()

    fsf.Data.Book.currSection = topSection + "." + subsecPath
    fsf.Data.Book.currTopSection = topSection

    lm.Wr.SectionLayout.set()

    mainMenuManager = dt.AppState.UIManagers.getData("fake token", wf.Wr.MenuManagers.MainMenuManager.__base__)
            
    mainMenuManager.switchToSectionLayout()

    # open pdf on the correct page
    ocf.Wr.PdfApp.openSubsectionPDF(positionIDX, topSection, subsecPath, bookName)

