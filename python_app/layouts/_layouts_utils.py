# import sys
# sys.path.append(os.getenv("BOOKS_PY_APP_PATH"))
import os
import _utils._utils_main as u

import Quartz
from AppKit import NSWorkspace

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

'''
osascript to manipulate windows:
tell application "Skim" to get properties of window id 66929
tell application "Skim" to set bounds of window id 66929 to {300, 30, 100, 1000}
tell application "Skim" to set visible of window id 66928 to false
'''
