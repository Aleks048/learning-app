import os
import subprocess
import tkinter as tk
from threading import Thread

import UI.widgets_vars as wv 
import UI.widgets_utils as wu
import UI.widgets_messages as wmes

import file_system.file_system_manager as fsm
import tex_file.tex_file_facade as tff

import _utils.logging as log
import _utils._utils_main as _u

import data.constants as d
import data.temp as dt
import scripts.osascripts as oscr

import outside_calls.outside_calls_facade as ocf

import UI.widgets_wrappers as ww
import UI.widgets_manager as wm




class StartupConfirm_BTN(ww.currUIImpl.Button):
    renderData = {
        ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 1},
        ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
    }
    text = "Start"
    name = "_startupConfirmBTN"

    def __init__(self, patentWidget, prefix):
        super().__init__(prefix, self.name, self.text, 
                        patentWidget, self.renderData, self.cmd)

    def cmd(self):
        self.name
        self.rootWidget.withdraw()
        _u.Settings.updateProperty(_u.Settings.PubProp.currLayout_ID, "Main")
        wm.MainMenuManager.createMenu(self.rootWidget)

class AddBook_BTN(ww.currUIImpl.Button):
    renderData = {
        ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 6},
        ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
    }
    text = "Add Book"
    name = "_addBookBTN"


    def __init__(self, patentWidget, prefix, BookMenuWidget):
        self.BookMenuWidget = BookMenuWidget

        super().__init__(prefix, self.name, self.text, 
                        patentWidget, self.renderData, self.cmd)
    
    def render(self, **kwargs):
        return super().render(**self.renderData)

    def cmd(self):
        bookPath = wv.StartupUItkVariables.newBookLocation.get()
        bookName = wv.StartupUItkVariables.newBookName.get()
        originalMaterialLocation = wv.StartupUItkVariables.originalMaterialLocation.get()
        originalMaterialName = wv.StartupUItkVariables.originalMaterialName.get()

        # create a directory
        try:
            os.makedirs(bookPath)
        except:
            message = "Could not create a filepath for new book: " + bookPath
            log.autolog(message)
            wmes.MessageMenu.createMenu(message)
            return
        
        # update settings
        _u.Settings.Book.addNewBook(bookName, bookPath)
        # set as current book
        _u.Settings.Book.setCurrentBook(bookName, bookPath)

        # create structures
        fsm.Wr.BookInfoStructure.createStructure()
        fsm.Wr.SectionInfoStructure.createStructure()
        fsm.Wr.TOCStructure.createStructure()
        fsm.Wr.OriginalMaterialStructure.createStructure()

        # add original material
        fsm.Wr.OriginalMaterialStructure.addOriginalMaterial(originalMaterialName, 
                                                            originalMaterialLocation, 
                                                            "")
        
        booksNames = list(_u.getListOfBooks()) 
        # wu.updateOptionMenuOptionsList(self.rootWidget, 
        #                                 "chooseBook_optionMenu", 
        #                                 booksNames, 
        #                                 wv.StartupUItkVariables.bookChoice,
        #                                 self.BookMenuWidget.cmd)

class ChooseStartupBook_OM(ww.currUIImpl.OptionMenu):
    renderData = {
        ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 0},
        ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
    }
    name = "_chooseBook_optionMenu"

    def __init__(self, patentWidget, prefix):
        self.listOfBooksNames = _u.getListOfBooks()

        super().__init__(prefix, self.name, self.listOfBooksNames,
                        patentWidget, self.renderData, self.cmd)
    
    def cmd(_):
        bookName = wv.StartupUItkVariables.bookChoice.get()
        bookPaths = _u.Settings.readProperty(_u.Settings.PubProp.booksPaths_ID)
        bookPath = bookPaths[bookName]
        _u.Settings.Book.setCurrentBook(bookName, bookPath)

class StrtupBookName_ETR(ww.currUIImpl.TextEntry):
    renderData = {
        ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 2},
        ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
    }
    extraBuildOptions = {
        ww.Data.GeneralProperties_ID : {ww.Data.CommonTextColor_ID: wu.Data.ENT.defaultTextColor},
        ww.TkWidgets.__name__ : {}
    }
    defaultText = "Book name"
    name = "_bookName"

    def __init__(self, patentWidget, prefix):
        super().__init__(prefix, 
                        self.name, 
                        patentWidget, 
                        self.renderData,
                        self.extraBuildOptions,
                        self.bindCmd)
        super().setData(self.defaultText)

    def bindCmd(self):
        self.widjetObj.bind(ww.currUIImpl.Data.BindID.focusIn,  
                        lambda *args: wu.addDefaultTextToETR(self))
        self.widgetObj.bind(ww.currUIImpl.Data.BindID.focusOut, 
                        lambda *args: wu.addDefaultTextToETR(self))

class StrtupBookLocation_ETR(ww.currUIImpl.TextEntry):
    renderData = {
        ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 3},
        ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
    }
    extraBuildOptions = {
        ww.Data.GeneralProperties_ID : {ww.Data.CommonTextColor_ID: wu.Data.ENT.defaultTextColor},
        ww.TkWidgets.__name__ : {}
    }
    defaultText = "Book location"
    name = "_bookLocation"

    def __init__(self, patentWidget, prefix):
        super().__init__(prefix, 
                        self.name, 
                        patentWidget, 
                        self.renderData,
                        self.extraBuildOptions,
                        self.bindCmd)
        super().setData(self.defaultText)

    def bindCmd(self):
        self.widjetObj.bind(ww.currUIImpl.Data.BindID.focusIn,  
                        lambda *args: wu.addDefaultTextToETR(self))
        self.widgetObj.bind(ww.currUIImpl.Data.BindID.focusOut, 
                        lambda *args: wu.addDefaultTextToETR(self))

class StrtupOriginalMaterialName_ETR(ww.currUIImpl.TextEntry):
    renderData = {
        ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 4},
        ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
    }
    extraBuildOptions = {
        ww.Data.GeneralProperties_ID : {ww.Data.CommonTextColor_ID: wu.Data.ENT.defaultTextColor},
        ww.TkWidgets.__name__ : {}
    }
    defaultText = "Original Material Name"
    name = "_originalMaterialName"

    def __init__(self, patentWidget, prefix):
        super().__init__(prefix, 
                        self.name, 
                        patentWidget, 
                        self.renderData,
                        self.extraBuildOptions,
                        self.bindCmd)
        super().setData(self.defaultText)

    def bindCmd(self):
        self.widjetObj.bind(ww.currUIImpl.Data.BindID.focusIn,  
                        lambda *args: wu.addDefaultTextToETR(self))
        self.widgetObj.bind(ww.currUIImpl.Data.BindID.focusOut, 
                        lambda *args: wu.addDefaultTextToETR(self))

class StrtupOriginalMaterialLocation_ETR(ww.currUIImpl.TextEntry):
    renderData = {
        ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 5},
        ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
    }
    extraBuildOptions = {
        ww.Data.GeneralProperties_ID : {ww.Data.CommonTextColor_ID: wu.Data.ENT.defaultTextColor},
        ww.TkWidgets.__name__ : {}
    }
    defaultText = "Original Material Locattion"
    name = "_originalMaterialLocattion"

    def __init__(self, patentWidget, prefix):
        super().__init__(prefix, 
                        self.name, 
                        patentWidget, 
                        self.renderData,
                        self.extraBuildOptions,
                        self.bindCmd)
        super().setData(self.defaultText)

    def bindCmd(self):
        self.widjetObj.bind(ww.currUIImpl.Data.BindID.focusIn,  
                        lambda *args: wu.addDefaultTextToETR(self))
        self.widgetObj.bind(ww.currUIImpl.Data.BindID.focusOut, 
                        lambda *args: wu.addDefaultTextToETR(self))