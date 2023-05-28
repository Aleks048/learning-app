import tkinter as tk

import UI.widgets_data as wd

import UI.widgets_wrappers as ww
import UI.widgets_collection.main.math.manager as mmm

import layouts.layouts_facade as lm
import data.constants as dc
import data.temp as dt

import settings.facade as sf

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
        # show UI main layout
        import generalManger.generalManger as gm
        
        gm.GeneralManger.startNonStartMenus()

        # show 3rd party main layout
        lm.Wr.MainLayout.set()

class AddBook_BTN(ww.currUIImpl.Button,
                  dc.AppCurrDataAccessToken):
    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 7},
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
        import generalManger.generalManger as gm

        # get the data from the ETRs
        bookPath = self.notify(StrtupBookLocation_ETR)
        bookName = self.notify(StrtupBookName_ETR)
        originalMaterialLocation = self.notify(StrtupOriginalMaterialLocation_ETR)
        originalMaterialRelPath = self.notify(StrtupOriginalMaterialRelPath_ETR)
        originalMaterialName = self.notify(StrtupOriginalMaterialName_ETR)

        if bookPath == StrtupBookLocation_ETR.defaultText:
            raise("Please provide bookpath")
        if bookName == StrtupBookName_ETR.defaultText:
            raise("Please provide bookName")
        if originalMaterialLocation == StrtupOriginalMaterialLocation_ETR.defaultText:
            raise("Please provide original material location")
        if originalMaterialName == StrtupOriginalMaterialName_ETR.defaultText:
            raise("Please provide original material name")
        if originalMaterialRelPath == StrtupOriginalMaterialRelPath_ETR.defaultText:
            originalMaterialRelPath = ""

        gm.GeneralManger.AddNewBook(bookName, 
                                    bookPath,
                                    originalMaterialLocation,
                                    originalMaterialRelPath,
                                    originalMaterialName)

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
        
        currBookName = sf.Wr.Manager.Book.getCurrBookName()
        self.setData(currBookName)
    
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
    defaultText = "Book name. (The name of the book in the system.)"

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        extraBuildOptions = {
            ww.Data.GeneralProperties_ID : {ww.Data.CommonTextColor_ID: wd.Data.ENT.defaultTextColor},
            ww.TkWidgets.__name__ : {}
        }
        name = "_bookName"

        super().__init__(prefix, 
                        name, 
                        patentWidget, 
                        renderData,
                        extraBuildOptions,
                        defaultText = self.defaultText)
        
        super().setData(self.defaultText)
    
        
    def receiveNotification(self, _):
        return self.getData()

class StrtupBookLocation_ETR(ww.currUIImpl.TextEntry):
    defaultText = "Book location. (folder where the book will be stored)"

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 3},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        extraBuildOptions = {
            ww.Data.GeneralProperties_ID : {ww.Data.CommonTextColor_ID: wd.Data.ENT.defaultTextColor},
            ww.TkWidgets.__name__ : {}
        }
        name = "_bookLocation"

        super().__init__(prefix, 
                        name, 
                        patentWidget, 
                        renderData,
                        extraBuildOptions,
                        defaultText = self.defaultText)
        
        super().setData(self.defaultText)
    
        
    def receiveNotification(self, _):
        return self.getData()

class StrtupOriginalMaterialRelPath_ETR(ww.currUIImpl.TextEntry):
    defaultText = "OM Rel Path (don't: st w '/' & incl book filename)"

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 4},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        extraBuildOptions = {
            ww.Data.GeneralProperties_ID : {ww.Data.CommonTextColor_ID: wd.Data.ENT.defaultTextColor},
            ww.TkWidgets.__name__ : {}
        }
        name = "_originalMaterialRelPath"

        super().__init__(prefix, 
                        name, 
                        patentWidget, 
                        renderData,
                        extraBuildOptions,
                        defaultText = self.defaultText)
        super().setData(self.defaultText)
    
        
    def receiveNotification(self, _):
        return self.getData()


class StrtupOriginalMaterialName_ETR(ww.currUIImpl.TextEntry):
    defaultText = "OM Name (internal not reflected in the file)"

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 5},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        extraBuildOptions = {
            ww.Data.GeneralProperties_ID : {ww.Data.CommonTextColor_ID: wd.Data.ENT.defaultTextColor},
            ww.TkWidgets.__name__ : {}
        }
        name = "_originalMaterialName"

        super().__init__(prefix, 
                        name, 
                        patentWidget, 
                        renderData,
                        extraBuildOptions,
                        defaultText = self.defaultText)
        super().setData(self.defaultText)
    
        
    def receiveNotification(self, _):
        return self.getData()

class StrtupOriginalMaterialLocation_ETR(ww.currUIImpl.TextEntry):
    defaultText = "OM Location. (Where to copy the file from)"

    def __init__(self, patentWidget, prefix):
        name = "_originalMaterialLocattion"
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 6},
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
                        defaultText = self.defaultText)
        super().setData(self.defaultText)
    
    def receiveNotification(self, _):
        return self.getData()

class StartupRoot(ww.currUIImpl.RootWidget):
    pass

