import Quartz
from AppKit import NSWorkspace

import os
import _utils._utils_main as _u
import file_system.file_system_main as fs
import UI.widgets_manager as uim


def moveApplicationsWindow(appName, windowID, bounds):
    bounds = [str(i) for i in bounds]
    osascript2 = "osascript -e '\
    tell application \"System Events\" to tell process \"" + appName + "\"\n\
	    tell window " + windowID + "\n\
		    set size to {" + bounds[0] + ", " + bounds[1] + "}\n\
		    set position to {" + bounds[2] + ", " + bounds[3] + "}\n\
            perform action \"AXRaise\"\n\
	    end tell\n\
    end tell'"
    os.system(osascript2)


def hideApplicationsWindow(appName, windowID):
    osascript = "osascript -e '\
    tell application \"" + appName + "\"\n\
        get properties of window id " + windowID + "\n\
        set visible of window id " + windowID + " to false\n\
    end tell'"
    os.system(osascript)


def openPdfInSkim(pathToChapterFolder):
    print("Opening in " + u.Settings.skim_ID + " pdf: " + pathToChapterFolder)
    osascript = "osascript -e '\n\
    tell application \"" + u.Settings.skim_ID + "\"\n\
        open \"" + pathToChapterFolder + "\"\n\
    end tell\n\
    '"
    _waitDummy = os.system(osascript)


def movePdfToPage(filename, page):
    osascript = "osascript -e '\n\
    tell application \"" + u.Settings.skim_ID + "\"\n\
        tell document \"" + filename + "\"\n\
    		go to page " + str(page) + "\n\
        end tell\n\
    end tell'"
    print("movePdfToPage - moving to page " + str(page))
    os.system(osascript)


def openChapterFolderInFinder(pathToChapterFolder):
    print("Opening in Finder chapter: " + pathToChapterFolder)
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
        openPdfInSkim(_u.Settings.Book.getWholeBookPath())
        ownerName, windowID = _u.getOwnersName_windowID_ofApp(_u.Settings._appsIDs.skim_ID, _u.Settings.PubProp.wholeBook_ID + ".pdf")
    
    if ownerName == None or windowID == None: 
        print("openWholeBook - Something went wrong. Skim could not open the document")
    else:
        moveApplicationsWindow(ownerName, windowID, [dimentions[0], dimentions[1], position[0] , position[1]])


def moveWholeBookToChapter():
    currChapter = fs.BookInfoStructure.readProperty(fs.BookInfoStructure.currSection_ID)
    
    if currChapter == "":
        message = "Could not move the book to page. currChapter is empty."
        uim.ShowMessageMenu.createMenu(message)
        print("moveWholeBookToChapter -" + message)
    else:
        chapterPage = _u.BookSettings.readProperty(_u.BookSettings.ChapterProperties.getChapterStartPagePropertyID(currChapter[2:]))
        
        if chapterPage == "":
            message = "Could not move the book to page. could not read chapterPage."  
            uim.ShowMessageMenu.createMenu(message)
            print("moveWholeBookToChapter - " + message)   
        else:
            movePdfToPage(_u.Settings.PubProp.wholeBook_ID + ".pdf", chapterPage)


'''
osascript to manipulate windows:
tell application "Skim" to get properties of window id 66929
tell application "Skim" to set bounds of window id 66929 to {300, 30, 100, 1000}
tell application "Skim" to set visible of window id 66928 to false
'''