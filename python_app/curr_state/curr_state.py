import os

class Data:
    class Book:
        """
        Book
        """
        pass

    class Section:
        """
        Section
        """
        pass

    class Settings:
        """
        Settings
        """
        currState_ID = "currentState"
        data = {
            currState_ID : None,
            currState_ID + "_BookPath": None,
            currState_ID + "_BookName": None,
            currState_ID + "_Layout": None,     
            currState_ID + "_ScreenshotLocation": None,
            "whole_book": None,
            "booksPaths": None
        }
    
# sectionPrefix = \
#     fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.sections_prefix_ID)
# sectionsPathSeparator = \
#     fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.sections_path_separator_ID)

# def getpageOfDoc():
#     activeApps = _u.getAllRunningApps()
    
#     app = [i for i in activeApps if _u.Settings._appsIDs.skim_ID in str(i).lower()][0]
#     if app == None :
#         log.autolog("skim was not found")
#         return -1
    
#     windowList = _u.getWindowsFromApp(app)
#     currChapter = Section.readCurrSection()
    
#     for window in windowList:
#         if window["kCGWindowOwnerName"] == app.localizedName():
#             if currChapter + "_main.pdf" in window["kCGWindowName"]:
#                 windowName = str(window["kCGWindowName"])
#                 pageNum = windowName.split("page ")[1]
#                 pageNum = pageNum.split(" ")[0]
#                 return pageNum
