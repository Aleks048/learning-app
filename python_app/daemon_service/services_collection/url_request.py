import outside_calls.pdfApp_calls as sc
import outside_calls.outside_calls_facade as ocf

import _utils.logging as log

import file_system.file_system_facade as fsf

import layouts.layouts_manager as lm

import data.constants as dc
import data.temp as dt

import UI.widgets_facade as wf

import scripts.osascripts as oscr



def processCall(url):
    log.autolog("Processing url request: '{0}'.".format(url))
    url = url.replace("KIK:/", "")
    url = url.split(".")
    bookName = url[0]
    topSection = url[1]
    subsecPath = url[2]
    positionIDX = url[3]

    # switch section
    fsf.Data.Book.currSection = topSection + "." + subsecPath
    fsf.Data.Book.currTopSection = topSection

    lm.Wr.SectionLayout.set()

    mainMenuManager = dt.AppState.UIManagers.getData("fake toke", wf.Wr.MenuManagers.MainMenuManager.__base__)
            
    mainMenuManager.switchToSectionLayout()

    # open pdf on the correct page
    ocf.Wr.PdfApp.openSubsectionPDF(positionIDX, topSection, subsecPath, bookName)

