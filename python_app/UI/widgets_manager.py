import os
import tkinter as tk
import threading

import UI.widgets_collection as wc
import UI.widgets_utils as wu
import UI.widgets_vars as wv
import UI.widgets_messages as wmes

import layouts.layouts_manager as lm

import file_system.file_system_manager as fsm

import _utils.logging as log
import _utils._utils_main as _u

class Data:
    UItkVariables = wv.UItkVariables

class Wr:
    class ConfirmationMenu(wmes.ConfirmationMenu):
        pass
    
    class MessageMenu(wmes.MessageMenu):
        pass

class StartupMenu:
    prefix = "_" + __name__

    monitorSize = _u.getMonitorSize()
    
    @classmethod
    def createMenu(cls, winRoot):
        cls.winRoot = tk.Toplevel(winRoot)
        wu.initVars.StartupUI()

        cls.winRoot.geometry("+" + str(int(cls.monitorSize[0] / 2)) \
                    + "+" \
                    + str(int(cls.monitorSize[1] / 2)))


        # get chooseBookOptionMenu
        def bookMenuChooseCallback():
            bookName = wv.StartupUItkVariables.bookChoice.get()
            bookPaths = _u.Settings.readProperty(_u.Settings.PubProp.booksPaths_ID)
            bookPath = bookPaths[bookName]
            _u.Settings.Book.setCurrentBook(bookName, bookPath)
        
        books_OM = wc.StartupMenu.getBookChoosing_OM(cls.winRoot, bookMenuChooseCallback)
        books_OM.pack()

        # get confirmation button
        def startup_BTN_callback():
            cls.winRoot.withdraw()
            MainMenu.createMenu(winRoot)
        confirm_BTN = wc.StartupMenu.getStartup_BTN(cls.winRoot, startup_BTN_callback)
        
        confirm_BTN.pack()
        
        entriesData = [
            ["bookName", wv.StartupUItkVariables.newBookName, "Book name"],
            ["bookLocation", wv.StartupUItkVariables.newBookLocation, "Book location"],
            ["originalMaterialName", wv.StartupUItkVariables.originalMaterialName, "Original Material Name"],
            ["originalMaterialLocattion", wv.StartupUItkVariables.originalMaterialLocation, "Original Material Locattion"]
        ]
        textEntries = []
        for entryData in entriesData:
            textEntry = wc.StartupMenu.getTextEntry_ETR(cls.winRoot, *entryData)
            textEntry.pack()

        def addBookCallback():
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
                wmes.messagebox(message)
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
            fsm.Wr.OriginalMaterialStructure.addOriginalMaterial(originalMaterialName, originalMaterialLocation, "")
            
            booksNames = list(_u.Settings.readProperty(_u.Settings.PubProp.booksPaths_ID).keys()) 
            wu.updateOptionMenuOptionsList(cls.winRoot, 
                                            "chooseBook_optionMenu", 
                                            booksNames, 
                                            wv.StartupUItkVariables.bookChoice,
                                            bookMenuChooseCallback)


        addbook_BTN = wc.StartupMenu.addNewBook_BTN(cls.winRoot, addBookCallback)
        addbook_BTN.pack()

        # assign the keys
        cls._bindKeys()
        
        # run the tk
        cls.winRoot.mainloop()

    @classmethod
    def _bindKeys(cls):
        cls.winRoot.bind("<Escape>", lambda e: cls.winRoot.destroy())
        cls.winRoot.bind("<Return>", lambda e: cls.winRoot.destroy())


class MainMenu:
    @classmethod
    def createMenu(cls, winRoot):
        cls.winRoot = tk.Toplevel(winRoot)
        wu.initVars.MainUI()

        wc.LayoutsMenus.SectionLayoutUI.addWidgets(cls.winRoot)
        wu.hideAllWidgets(cls.winRoot)
        wc.SectionsUI.setSectionsUI(cls.winRoot)
        wu.hideAllWidgets(cls.winRoot)
        wc.LayoutsMenus.MainLayoutUI.addWidgets(cls.winRoot)
        _u.Settings.UI.showMainWidgetsNext = False

        #set Layout
        menuDimensions = wc.LayoutsMenus.MainLayoutUI.pyAppDimensions
        lm.Wr.MainLayout.set(cls.winRoot, *menuDimensions)

        cls.winRoot.mainloop()
        