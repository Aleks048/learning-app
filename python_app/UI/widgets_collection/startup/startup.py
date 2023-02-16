import os
import subprocess
import tkinter as tk
from threading import Thread

import UI.widgets_vars as wv 
import UI.widgets_utils as wu
import UI.widgets_data as wd
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
import UI.widgets_collection.main.math.manager as wm




class StartupConfirm_BTN(ww.currUIImpl.Button):

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        text = "Start"
        name = "_startupConfirmBTN"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        self.name
        self.rootWidget.stopMainLoop()
        _u.Settings.updateProperty(_u.Settings.PubProp.currLayout_ID, "Main")
        wm.MathMenuManager.createMenu()

class AddBook_BTN(ww.currUIImpl.Button):
    def __init__(self, patentWidget, prefix, BookMenuWidget):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 6},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        text = "Add Book"
        name = "_addBookBTN"

        self.BookMenuWidget = BookMenuWidget

        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

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

        self.notifyAllListeners()

class ChooseStartupBook_OM(ww.currUIImpl.OptionMenu):

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 0},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_chooseBook_optionMenu"
        self.listOfBooksNames = _u.getListOfBooks()

        super().__init__(prefix, 
                        name, 
                        self.listOfBooksNames,
                        patentWidget, 
                        renderData, 
                        self.cmd)
    
    def cmd(self):
        bookName = self.getData()
        bookPath = _u.Settings.Book.getPathFromName(bookName)
        _u.Settings.Book.setCurrentBook(bookName, bookPath)
        
        self.notifyAllListeners()
    
    def notify(self, _):
        booksNames = list(_u.getListOfBooks()) 
        self.updateOptions(booksNames)

class StrtupBookName_ETR(ww.currUIImpl.TextEntry):

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        extraBuildOptions = {
            ww.Data.GeneralProperties_ID : {ww.Data.CommonTextColor_ID: wd.Data.ENT.defaultTextColor},
            ww.TkWidgets.__name__ : {}
        }
        defaultText = "Book name"
        name = "_bookName"

        super().__init__(prefix, 
                        name, 
                        patentWidget, 
                        renderData,
                        extraBuildOptions,
                        self.bindCmd,
                        defaultText)
        super().setData(self.defaultText)

    def bindCmd(self):
        self.widjetObj.bind(ww.currUIImpl.Data.BindID.focusIn,
                        lambda *args: addDefaultTextToETR(self))
        self.widgetObj.bind(ww.currUIImpl.Data.BindID.focusOut, 
                        lambda *args: addDefaultTextToETR(self))

class StrtupBookLocation_ETR(ww.currUIImpl.TextEntry):

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 3},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        extraBuildOptions = {
            ww.Data.GeneralProperties_ID : {ww.Data.CommonTextColor_ID: wd.Data.ENT.defaultTextColor},
            ww.TkWidgets.__name__ : {}
        }
        defaultText = "Book location"
        name = "_bookLocation"

        super().__init__(prefix, 
                        name, 
                        patentWidget, 
                        renderData,
                        extraBuildOptions,
                        self.bindCmd,
                        defaultText)
        super().setData(self.defaultText)

    def bindCmd(self):
        self.widjetObj.bind(ww.currUIImpl.Data.BindID.focusIn,  
                        lambda *args: addDefaultTextToETR(self))
        self.widgetObj.bind(ww.currUIImpl.Data.BindID.focusOut, 
                        lambda *args: addDefaultTextToETR(self))

class StrtupOriginalMaterialName_ETR(ww.currUIImpl.TextEntry):

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 4},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        extraBuildOptions = {
            ww.Data.GeneralProperties_ID : {ww.Data.CommonTextColor_ID: wd.Data.ENT.defaultTextColor},
            ww.TkWidgets.__name__ : {}
        }
        defaultText = "Original Material Name"
        name = "_originalMaterialName"

        super().__init__(prefix, 
                        name, 
                        patentWidget, 
                        renderData,
                        extraBuildOptions,
                        self.bindCmd,
                        defaultText)
        super().setData(defaultText)

    def bindCmd(self):
        self.widjetObj.bind(ww.currUIImpl.Data.BindID.focusIn,  
                        lambda *args: addDefaultTextToETR(self))
        self.widgetObj.bind(ww.currUIImpl.Data.BindID.focusOut, 
                        lambda *args: addDefaultTextToETR(self))

class StrtupOriginalMaterialLocation_ETR(ww.currUIImpl.TextEntry):

    def __init__(self, patentWidget, prefix):
        name = "_originalMaterialLocattion"
        defaultText = "Original Material Locattion"
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 5},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        extraBuildOptions = {
            ww.Data.GeneralProperties_ID : {ww.Data.CommonTextColor_ID: wd.Data.ENT.defaultTextColor},
            ww.TkWidgets.__name__ : {}
        }

        super().__init__(prefix, 
                        name, 
                        patentWidget, 
                        renderData,
                        extraBuildOptions,
                        self.bindCmd,
                        defaultText)
        super().setData(defaultText)

    def bindCmd(self):
        self.widjetObj.bind(ww.currUIImpl.Data.BindID.focusIn,  
                        lambda *args: addDefaultTextToETR(self))
        self.widgetObj.bind(ww.currUIImpl.Data.BindID.focusOut, 
                        lambda *args: addDefaultTextToETR(self))

class StartupRoot(ww.currUIImpl.RootWidget):
    pass


def addDefaultTextToETR(widget):
    current = widget.getData()
    if current == widget.defaultText:
        widget.setTextColor(wd.Data.ENT.regularTextColor)
        widget.setData("")
    elif current == "":
        widget.setTextColor(wd.Data.ENT.defaultTextColor)
        widget.setData(widget.defaultText)