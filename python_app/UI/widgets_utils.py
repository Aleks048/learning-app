import tkinter as tk
import os

import UI.widgets_vars as wv

import file_system.file_system_manager as fsm
import layouts.layouts_manager as lm

import _utils._utils_main as _u
import _utils.logging as log

class Data:
    class ENT:
        entryWidget_ID = "ETR"

        regularTextColor = "white"
        defaultTextColor = "blue"

class Screenshot:
        
    def getValueScreenshotLocation():
        relPath =  fsm.Wr.Paths.Screenshot.getRel_curr()
        log.autolog(relPath)
        return "dir: " + relPath if relPath != "" else "No direction yet."


    def setValueScreenshotLoaction():
        wv.UItkVariables.scrshotPath.set(fsm.Wr.Paths.Screenshot.getRel_curr())


    @classmethod
    def getText_CurrentScreenshotDirWidget(cls, mainWinRoot, namePref = ""):
        canvas= tk.Canvas(mainWinRoot,
                        name = namePref.lower() + "_showCurrScreenshotLocation_text", 
                        width=520, 
                        height= 25)

        currScrshDir = wv.UItkVariables.scrshotPath

        currScrshDir.set(cls.getValueScreenshotLocation())
        
        txt = canvas.create_text(30, 10, anchor="nw", text=currScrshDir.get())

        def on_change(varname, index, mode):
            canvas.itemconfigure(txt, text=cls.getValueScreenshotLocation())
        
        currScrshDir.trace_variable('w', on_change)

        return canvas

def updateOptionMenuOptionsList(mainWinRoot, menuID, newMenuOptions, choiceVar, callback):
    def subsectionChoosingCallback(value):
        choiceVar.set(value)
        callback(mainWinRoot)

    if newMenuOptions == None:
        # TODO: should check what conditions lead to None newMenuOptions
        return
    
    if newMenuOptions[0].isnumeric():
        newMenuOptions.sort()
    
    for e in mainWinRoot.winfo_children():
        if menuID in e._name:
            for om in e.winfo_children():
                om['menu'].delete(0, 'end')
                for choice in newMenuOptions:
                    om['menu'].add_command(label=choice, 
                                        command= lambda value=choice: subsectionChoosingCallback(value))
                    choiceVar.set(newMenuOptions[0])


def getSubsectionsListForCurrTopSection():
    currSectionPath = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.currTopSection_ID)
    childrensList = fsm.getSubsectionsList(currSectionPath)
    return childrensList


def addDefaultTextToETR(entry, dataVar, defaultText):
    current = dataVar.get()
    
    if current == defaultText:
        entry.configure(fg = Data.ENT.regularTextColor)
        dataVar.set("")
    elif current == "":
        entry.configure(fg = Data.ENT.defaultTextColor)
        dataVar.set(defaultText)


def hideAllWidgets(mainWinRoot):
    '''
    hide all widgets. clear all entries
    '''
    for e in mainWinRoot.winfo_children():
        # clear all entries
        if (Data.ENT.entryWidget_ID in e._name):
            if ("_imageGeneration_" not in e._name):
                e.delete(0, 'end')
        e.grid_remove()


def showCurrentLayout(mainWinRoot, menuWidth, menuHeight):
    #TODO: need to be reworked
    l_Name = _u.Settings.readProperty(_u.Settings.PubProp.currLayout_ID)
    
    layoutClass = [i for i in lm.Data.listOfLayoutClasses if i.__name__.replace(_u.Settings.layoutClassToken,"") == l_Name][0]
    log.autolog("Hippo Showing layout: \n" 
                + str(menuWidth) + "\n" 
                + str(menuHeight) + "\n" 
                + layoutClass.__name__)
    
    layoutClass.set(mainWinRoot, menuWidth, menuHeight)
    hideAllWidgets(mainWinRoot)


    for e in mainWinRoot.winfo_children():
        if layoutClass.__name__.lower() in e._name:
            if (Data.ENT.entryWidget_ID in e._name):
                e.focus_set()
            e.grid()

class initVars:
    def MainUI():
        wv.UItkVariables.needRebuild = tk.BooleanVar()

        wv.UItkVariables.buttonText = tk.StringVar()
        wv.UItkVariables.imageGenerationEntryText = tk.StringVar()

        wv.UItkVariables.createTOCVar = tk.BooleanVar()
        wv.UItkVariables.TOCWithImageVar = tk.BooleanVar()
        
        wv.UItkVariables.topSection = tk.StringVar()
        wv.UItkVariables.subsection = tk.StringVar()

        wv.UItkVariables.scrshotPath = tk.StringVar()
        
        wv.UItkVariables.currCh = tk.StringVar()
        wv.UItkVariables.currSubch = tk.StringVar()

        wv.UItkVariables.glLinkTargetImLink = tk.StringVar()
        wv.UItkVariables.glLinktargetSections = tk.StringVar()
        wv.UItkVariables.glLinkSourceImLink = tk.StringVar()

    def StartupUI():
        wv.StartupUItkVariables.bookChoice = tk.StringVar()
        wv.StartupUItkVariables.newBookName = tk.StringVar()
        wv.StartupUItkVariables.newBookLocation = tk.StringVar()
        wv.StartupUItkVariables.originalMaterialLocation = tk.StringVar()
        wv.StartupUItkVariables.originalMaterialName= tk.StringVar()