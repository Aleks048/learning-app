from _utils._utils_main import Settings, getPathToBooks, getMonitorSize
import tkinter as tk
from layouts import layouts_main

import UI.widgets_main as ui


def createMainWindow(position):
    mainWinRoot = tk.Tk()

    listOfLayouts = Settings.readProperty(Settings.layouts_ID)
    listOfLayoutClasses = [getattr(layouts_main, layoutName + Settings.layoutClass_ID) for layoutName in listOfLayouts]
   
    print("* createMainWindow - setting up Layouts UI")
    for layoutClass in listOfLayoutClasses:
        layoutClass.setUIElements(mainWinRoot)
    
    print("* createMainWindow - setting up Chapters UI")
    ui.SectionsUI.setSectionsUI(mainWinRoot)


    ui.UIWidgets.hideAllWidgets(mainWinRoot)
    
    ui.UIWidgets.getOptionsMenu_Layouts(mainWinRoot).grid(row=0,column=0)

    #move menu to the top center
    # mainWinRoot.geometry(str(position[0]) + "x100" + "+" + str(position[0]) + "+" + str(position[1]))
    mainWinRoot.geometry("+" + str(position[0]) + "+" + str(position[1]))

    return mainWinRoot

if __name__=="__main__":
    createMainWindow().mainloop()