import time
import os

import _utils.logging as log

import file_system.file_system_facade as fsf

import _utils._utils_main as _u


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

    if positionIDX == _u.Token.NotDef.str_t:
        positionIDX = fsf.Wr.Links.ImIDX.get(subsecPath)

    # switch section
    if not (subsecPath == fsf.Data.Book.currSection):
        fsf.Data.Book.currSection = subsecPath
        fsf.Data.Book.currTopSection = topSection

        # UI
        # mainMenuManager = dt.AppState.UIManagers.getData("fake data access token", 
        #                                                 wf.Wr.MenuManagers.MathMenuManager.__base__)
        # mainMenuManager.switchToSectionLayout()
