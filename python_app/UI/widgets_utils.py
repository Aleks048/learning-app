import tkinter as tk
import os

import UI.widgets_vars as wv
import _utils._utils_main as _u
import file_system.file_system_main as fs
import file_system.file_system_manager as fsm
import layouts.layouts_manager as lm

class Screenshot:
        
    def getValueScreenshotLocation():
        prefix = "dir: "
        if wv.UItkVariables.scrshotPath.get() == "":
            return prefix + _u.getCurrentScreenshotRelDir()
        else:
            return prefix + wv.UItkVariables.scrshotPath.get()


    def setValueScreenshotLoaction():
        print()
        wv.UItkVariables.scrshotPath.set(_u.getCurrentScreenshotRelDir())


    @classmethod
    def getText_CurrentScreenshotDirWidget(cls, mainWinRoot, namePref = ""):
        canvas= tk.Canvas(mainWinRoot,name = namePref.lower() + "_showCurrScreenshotLocation_text", width=520, height= 25)

        wv.UItkVariables.scrshotPath = tk.StringVar()
        currScrshDir = wv.UItkVariables.scrshotPath

        currScrshDir.set(cls.getValueScreenshotLocation())
        
        txt = canvas.create_text(30, 10, anchor="nw", text=currScrshDir.get())

        def on_change(varname, index, mode):
            canvas.itemconfigure(txt, text=cls.getValueScreenshotLocation())
        
        currScrshDir.trace_variable('w', on_change)

        return canvas

def _updateOptionMenuOptionsList(mainWinRoot, menuID, newMenuOptions, callback):
    def subsectionChoosingCallback(value):
        wv.UItkVariables.subsection.set(value)
        callback()

    for e in mainWinRoot.winfo_children():
        if menuID in e._name:
            for om in e.winfo_children():
                om['menu'].delete(0, 'end')
                for choice in newMenuOptions:
                    om['menu'].add_command(label=choice, 
                                        command= lambda value=choice: subsectionChoosingCallback(value))
                    wv.UItkVariables.subsection.set(newMenuOptions[0])

def _getSubsectionsListForCurrTopSection():
    currSectionPath = fs.BookInfoStructure.readProperty(fs.BookInfoStructure.PubProp.currTopSection_ID)
    print("hop")
    print(currSectionPath)
    childrensList = fsm.getSubsectionsList(currSectionPath)
    return childrensList

entryWidget_ID = "ETR"

def hideAllWidgets(mainWinRoot):
    '''
    hide all widgets. clear all entries
    '''
    for e in mainWinRoot.winfo_children():
        # clear all entries
        if (entryWidget_ID in e._name):
            if ("_imageGeneration_" not in e._name):
                e.delete(0, 'end')
        e.grid_remove()


def showCurrentLayout(mainWinRoot):
    #TODO: need to be reworked
    l_Name = _u.Settings.readProperty(_u.Settings.PubProp.currLayout_ID)
    layoutClass = [i for i in lm.listOfLayoutClasses if i.__name__.replace(_u.Settings.PubProp.currLayout_ID,"") == l_Name][0]
    layoutClass.set(mainWinRoot)
    hideAllWidgets(mainWinRoot)

    for e in mainWinRoot.winfo_children():
        if layoutClass.__name__.lower() in e._name:
            if (entryWidget_ID in e._name):
                e.focus_set()
            e.grid()