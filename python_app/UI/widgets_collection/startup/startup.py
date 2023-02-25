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


import layouts.layouts_manager as lm


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
        lm.Wr.MainLayout.set()
        wm.MathMenuManager.startManager()

class AddBook_BTN(ww.currUIImpl.Button):
    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 6},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        text = "Add Book"
        name = "_addBookBTN"

        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        bookPath = self.notify(StrtupBookLocation_ETR)
        bookName = self.notify(StrtupBookName_ETR)
        originalMaterialLocation = self.notify(StrtupOriginalMaterialLocation_ETR)
        originalMaterialName = self.notify(StrtupOriginalMaterialName_ETR)

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

        self.notify(ChooseStartupBook_OM)

class ChooseStartupBook_OM(ww.currUIImpl.OptionMenu):

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 0},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_chooseBook_optionMenu"
        self.listOfBooksNames = list(_u.getListOfBooks())

        super().__init__(prefix = prefix, 
                        name =name, 
                        rootWidget = patentWidget, 
                        renderData = renderData, 
                        cmd = self.cmd,
                        listOfOptions = self.listOfBooksNames)
        
        self.setData(self.listOfBooksNames[-1])
    
    def cmd(self):
        bookName = self.getData()
        bookPath = _u.Settings.Book.getPathFromName(bookName)
        _u.Settings.Book.setCurrentBook(bookName, bookPath)
        
        self.notifyAllListeners()
    
    def receiveNotification(self, _):
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
                        defaultText = defaultText)
        
        super().setData(self.defaultText)
    
        
    def receiveNotification(self, _):
        return self.getData()

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
                        defaultText = defaultText)
        
        super().setData(self.defaultText)
    
        
    def receiveNotification(self, _):
        return self.getData()

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
                        defaultText = defaultText)
        super().setData(defaultText)
    
        
    def receiveNotification(self, _):
        return self.getData()

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
                        defaultText = defaultText)
        super().setData(defaultText)
    
    def receiveNotification(self, _):
        return self.getData()

class StartupRoot(ww.currUIImpl.RootWidget):
    pass

