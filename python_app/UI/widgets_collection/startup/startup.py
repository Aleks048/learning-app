import os
import tkinter as tk

import UI.widgets_data as wd
import file_system.file_system_facade as fsf

import _utils.logging as log
import _utils._utils_main as _u

import UI.widgets_wrappers as ww
import UI.widgets_collection.main.math.manager as mmm
import UI.widgets_collection.message.manager as mesm
import UI.widgets_collection.startup.manager as stm


import layouts.layouts_manager as lm
import data.constants as dc
import data.temp as dt

import settings.facade as sf

import generalManger.generalManger as gm

class StartupConfirm_BTN(ww.currUIImpl.Button,
                         dc.AppCurrDataAccessToken):
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
        # # hide startup UI layout
        # startupManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
        #                                                 stm.StartupMenuManager)
        # startupManager.hide()
        
        # show 3rd party main layout
        lm.Wr.MainLayout.set()

        # show UI main layout
        mainMathManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                        mmm.MathMenuManager)
        mainMathManager.showOnly()

class AddBook_BTN(ww.currUIImpl.Button,
                  dc.AppCurrDataAccessToken):
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
        # get the data from the ETRs
        bookPath = self.notify(StrtupBookLocation_ETR)
        bookName = self.notify(StrtupBookName_ETR)
        originalMaterialLocation = self.notify(StrtupOriginalMaterialLocation_ETR)
        originalMaterialRelPath = self.notify(StrtupOriginalMaterialRelPath_ETR)

        gm.GeneralManger.AddNewBook(bookName, 
                                    bookPath,
                                    originalMaterialLocation,
                                    originalMaterialRelPath)

        # update choosing book OM
        self.notify(ChooseStartupBook_OM)

class ChooseStartupBook_OM(ww.currUIImpl.OptionMenu):

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 0},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_chooseBook_optionMenu"
        self.listOfBooksNames = list(sf.Wr.Manager.Book.getListOfBooksNames())

        super().__init__(prefix = prefix, 
                        name =name, 
                        rootWidget = patentWidget, 
                        renderData = renderData, 
                        cmd = self.cmd,
                        listOfOptions = self.listOfBooksNames)
        
        self.setData(self.listOfBooksNames[-1])
    
    def cmd(self):
        bookName = self.getData()
        bookPath = sf.Wr.Manager.Book.getPathFromName(bookName)
        sf.Wr.Manager.Book.setCurrentBook(bookName, bookPath)
        
        self.notifyAllListeners()
    
    def receiveNotification(self, _):
        booksNames = list(sf.Wr.Manager.Book.getListOfBooksNames()) 
        self.updateOptions(booksNames)

'''
next 4 ETRs are containers for data from the user
'''

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

class StrtupOriginalMaterialRelPath_ETR(ww.currUIImpl.TextEntry):

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
