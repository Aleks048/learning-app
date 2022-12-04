import os

# import file_system.file_system_manager as fsm
import _utils._utils_main as _u
import _utils.logging as log

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
#             if currChapter + "_main.myPDF" in window["kCGWindowName"]:
#                 windowName = str(window["kCGWindowName"])
#                 pageNum = windowName.split("page ")[1]
#                 pageNum = pageNum.split(" ")[0]
#                 return pageNum
