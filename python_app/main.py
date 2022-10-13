import tkinter as tk

from UI.widgets import *
import file_system
from file_system.file_system_main import BookInfoStructure
from layouts.layouts_main import *
from _utils._utils_main import *
from layouts import *
from file_system import *


def createMainWindow(position):
    mainWinRoot = tk.Tk()

    listOfLayouts = Settings.readProperty(Settings.layouts_ID)
    listOfLayoutClasses = [getattr(layouts_main, layoutName + Settings.layoutClass_ID) for layoutName in listOfLayouts]
   
    print("* createMainWindow - setting up Layouts UI")
    for layoutClass in listOfLayoutClasses:
        layoutClass.setUIElements(mainWinRoot)
    
    print("* createMainWindow - setting up Chapters UI")
    ChaptersUI.setChaptersUI(mainWinRoot)


    UIWidgets.hideAllWidgets(mainWinRoot)
    
    UIWidgets.getOptionsMenu_Layouts(mainWinRoot).grid(row=0,column=0)

    #move menu to the top center
    # mainWinRoot.geometry(str(position[0]) + "x100" + "+" + str(position[0]) + "+" + str(position[1]))
    mainWinRoot.geometry("+" + str(position[0]) + "+" + str(position[1]))

    return mainWinRoot


#startof the application
screenHalfWidth, _ = getMonitorSize()
screenHalfWidth = str(int(screenHalfWidth / 2))
mainWin = createMainWindow([screenHalfWidth,0])
mainWin.mainloop()
