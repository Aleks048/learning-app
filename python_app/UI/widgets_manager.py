import os
import tkinter as tk
import threading

import UI.widgets_collection as wc
import UI.widgets_utils as wu
import UI.widgets_vars as wv
import UI.widgets_messages as wmes

import layouts.layouts_manager as lm

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
    def createMenu(cls):

        cls.winRoot = tk.Tk()

        cls.winRoot.geometry("+" + str(int(cls.monitorSize[0] / 2)) \
                    + "+" \
                    + str(int(cls.monitorSize[1] / 2)))


        # get chooseBookOptionMenu
        def bookMenuChooseCallback(bookNameStVar):
            bookName = bookNameStVar.get()
            bookPaths = _u.Settings.readProperty(_u.Settings.PubProp.booksPaths_ID)
            bookPath = bookPaths[bookName]
            _u.Settings.Book.setCurrentBook(bookName, bookPath)
        
        books_OM = wc.StartupMenu.getBookChoosing_OM(cls.winRoot, bookMenuChooseCallback)
        books_OM.pack()

        # get confirmation button
        def startup_BTN_callback():
            cls.winRoot.destroy()
            MainMenu.createMenu()
        confirm_BTN = wc.StartupMenu.getStartup_BTN(cls.winRoot, startup_BTN_callback)
        
        confirm_BTN.pack()
        
        # get confirmation button
        confirm_BTN.pack()
        
        def addBookCallback():
            pass

        addbook_BTN = wc.StartupMenu.addNewBook_BTN(cls.winRoot, addBookCallback)
        
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
    def createMenu(cls):
        cls.winRoot = tk.Tk()
        wu.initUIvars()

        wc.LayoutsMenus.SectionLayoutUI.addWidgets(cls.winRoot)
        wu.hideAllWidgets(cls.winRoot)
        wc.SectionsUI.setSectionsUI(cls.winRoot)
        wu.hideAllWidgets(cls.winRoot)
        wc.LayoutsMenus.MainLayoutUI.addWidgets(cls.winRoot)
        _u.Settings.UI.showMainWidgets = True

        #set Layout
        menuDimensions = wc.LayoutsMenus.MainLayoutUI.pyAppDimensions
        lm.Wr.MainLayout.set(MainMenu.winRoot, *menuDimensions)

        cls.winRoot.mainloop()
        