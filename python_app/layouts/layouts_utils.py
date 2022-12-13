from AppKit import NSWorkspace
import os

import _utils._utils_main as _u
import _utils.logging as log
import file_system.file_system_manager as fsm
import UI.widgets_manager as uim

def moveApplicationsWindow(appName, windowID, bounds):
    bounds = [str(i) for i in bounds]
    osascript = "osascript -e '\
    tell application \"System Events\" to tell process \"" + appName + "\"\n\
	    tell window " + windowID + "\n\
		    set size to {" + bounds[0] + ", " + bounds[1] + "}\n\
		    delay 0.1\n\
            set position to {" + bounds[2] + ", " + bounds[3] + "}\n\
            delay 0.1\n\
            perform action \"AXRaise\"\n\
	    end tell\n\
    end tell'"
    os.system(osascript)

def hideApplicationsWindow(appName, windowID):
    osascript = "osascript -e '\
    tell application \"" + appName + "\"\n\
        get properties of window id " + windowID + "\n\
        set visible of window id " + windowID + " to false\n\
    end tell'"
    os.system(osascript)

def openPdfInSkim(pathToSectionFolder):
    log.autolog("Opening in '" + _u.Settings._appsIDs.skim_ID + "' pdf: " + pathToSectionFolder)
    osascript = "osascript -e '\n\
    tell application \"" + _u.Settings._appsIDs.skim_ID + "\"\n\
        open \"" + pathToSectionFolder + "\"\n\
    end tell\n\
    '"
    _waitDummy = os.system(osascript)

def movePdfToPage(filename, page):
    osascript = "osascript -e '\n\
    tell application \"" + _u.Settings._appsIDs.skim_ID + "\"\n\
        tell document \"" + filename + "\"\n\
    		go to page " + str(page) + "\n\
        end tell\n\
    end tell'"
    log.autolog("moving to page: " + str(page))
    os.system(osascript)

def openChapterFolderInFinder(pathToChapterFolder):
    log.autolog("Opening in Finder chapter: " + pathToChapterFolder)
    osascript = "osascript -e '\n\
    tell application \"Finder\"\n\
        open (\"" + pathToChapterFolder + "\" as POSIX file)\n\
    end tell\n\
    '"
    _waitDummy = os.system(osascript)

def vsCodeManipulation(clearWindows, collapseFolders, hide):
    osascript = "osascript -e '\
            tell application \"System Events\" \n\
                tell process \"" + _u.Settings._appsIDs.vsCode_ID + "\" to tell window 1\n\
                    perform action \"AXRaise\"\n\
                end tell\n\
                activate  application \"" + _u.Settings._appsIDs.vsCode_ID + "\"\n"
    if clearWindows:
        osascript += "keystroke \"kw\" using {command down}\n"
    if collapseFolders:
        osascript += "keystroke \"op\" using {command down}\n"
    if hide:
        osascript += "keystroke \"m\" using {command down}\n"
    osascript +="end tell'"
    return osascript

def openWholeBook(dimentions, position):
    # whole book in skim
    ownerName, windowID = _u.getOwnersName_windowID_ofApp(_u.Settings._appsIDs.skim_ID, _u.Settings.PubProp.wholeBook_ID + ".pdf")
    
    if ownerName == None or windowID == None:
        # if the book was not opened in Skim already    
        openPdfInSkim(fsm.Wr.OriginalMaterialStructure._getBaseAbsPath())
        ownerName, windowID = _u.getOwnersName_windowID_ofApp(_u.Settings._appsIDs.skim_ID, _u.Settings.PubProp.wholeBook_ID + ".pdf")
    
    if ownerName == None or windowID == None: 
        log.autolog("Something went wrong. Skim could not open the document")
    else:
        moveApplicationsWindow(ownerName, windowID, [dimentions[0], dimentions[1], position[0] , position[1]])

def moveWholeBookToChapter():
    currChapter = fsm.Wr.SectionCurrent.readCurrSection()
    
    if currChapter == "":
        message = "Could not move the book to page. currChapter is empty."
        uim.Wr.MessageMenu.createMenu(message)
        log.autolog(message)
    else:
        sectionPage = fsm.Wr.SectionInfoStructure.readProperty(fsm.PropIDs.Sec.startPage_ID)
        
        if sectionPage == "":
            message = "Could not move the book to page. could not read chapterPage."  
            uim.Wr.MessageMenu.createMenu(message)
            log.autolog(message)   
        else:
            movePdfToPage(_u.Settings.PubProp.wholeBook_ID + ".pdf", sectionPage)

'''
osascript to manipulate windows:
tell application "Skim" to get properties of window id 66929
tell application "Skim" to set bounds of window id 66929 to {300, 30, 100, 1000}
tell application "Skim" to set visible of window id 66928 to false
'''
