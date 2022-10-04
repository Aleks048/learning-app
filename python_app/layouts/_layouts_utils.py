import sys
import os
from time import sleep
sys.path.append(os.getenv("BOOKS_PY_APP_PATH"))
from _utils import _utils

import Quartz
from AppKit import NSWorkspace

def getWindowsFromApp(app):
    # if app.isActive():
    options = Quartz.kCGWindowListOptionOnScreenOnly
    return Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)

def getAllRunningApps():
    #get all the running applications
    workspace = NSWorkspace.sharedWorkspace()
    activeApps = workspace.runningApplications()
    return activeApps

def getOwnersName_windowID_ofApp(appName, windowIdentifier = ""):
    activeApps = getAllRunningApps()
    
    app = [i for i in activeApps if appName in str(i).lower()][0]
    if app == None :
        print ("getOwnersName_windowID_ofApp - the app was not found")
        return None, None
    
    windowList = getWindowsFromApp(app)
    windowIndex = 1
    
    for window in windowList:
        if window["kCGWindowOwnerName"] == app.localizedName():
            if windowIdentifier in window["kCGWindowName"]:
                ownerName = str(window["kCGWindowOwnerName"])
                windowID = str(windowIndex)

                return ownerName, windowID
            windowIndex += 1
    
    print("getOwnersName_windowID_ofApp - window was not found")
    return None, None

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
    print("Opening in " + _utils.Settings.skim_ID + " pdf: " + pathToChapterFolder)
    osascript = "osascript -e '\n\
    tell application \"" + _utils.Settings.skim_ID + "\"\n\
        open \"" + pathToChapterFolder + "\"\n\
    end tell\n\
    '"
    _waitDummy = os.system(osascript)

def movePdfToPage(filename, page):
    osascript = "osascript -e '\n\
    tell application \"" + _utils.Settings.skim_ID + "\"\n\
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
    # sleep(0.1)






# ownerName, windowID = getOwnersName_windowID_ofApp("skim", "3.7")
# moveApplicationsWindow(ownerName, windowID, [30, 30 , 500 , 200])
# # hideApplicationsWindow(ownerName, windowID)
# ownerName, windowID = getOwnersName_windowID_ofApp("vscode")
# moveApplicationsWindow(ownerName, windowID, [30, 30 , 500 , 200])
# hideApplicationsWindow(ownerName, windowID)



'''
osascript to manipulate windows:
tell application "Skim" to get properties of window id 66929
tell application "Skim" to set bounds of window id 66929 to {300, 30, 100, 1000}
tell application "Skim" to set visible of window id 66928 to false
'''
