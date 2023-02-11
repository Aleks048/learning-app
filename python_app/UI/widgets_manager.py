import os
import tkinter as tk
import threading

import UI.widgets_collection_old as wc
import UI.widgets_utils as wu
import UI.widgets_vars as wv
import UI.widgets_messages as wmes

import layouts.layouts_manager as lm

import file_system.file_system_manager as fsm

import _utils.logging as log
import _utils._utils_main as _u

import UI.widgets_collection.imageCreation as icw
import UI.widgets_collection.startup as sw


class MenuManager_Interface:
    def createMenu(cls, winRoot):
        raise NotImplementedError()
    
    @classmethod
    def _bindKeys(cls):
        raise NotImplementedError()


class MainMenuManager(MenuManager_Interface):
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
    

    @classmethod
    def _bindKeys(cls):
        pass


class StartupMenuManager(MenuManager_Interface):
    prefix = "_StartupMenu_"

    monitorSize = _u.getMonitorSize()
    
    @classmethod
    def createMenu(cls, winRoot):
        cls.winRoot = tk.Toplevel(winRoot)
        wu.initVars.StartupUI()

        cls.winRoot.geometry("+" + str(int(cls.monitorSize[0] / 2)) \
                    + "+" \
                    + str(int(cls.monitorSize[1] / 2)))
        
        books_OM = sw.ChooseStartupBook_OM(cls.winRoot, cls.prefix)
        books_OM.render()

        confirm_BTN = sw.StartupConfirm_BTN(cls.winRoot, cls.prefix)
        confirm_BTN.render()
        
        bookName_ETR = sw.StrtupBookName_ETR(cls.winRoot, cls.prefix)
        bookName_ETR.render()
        bookLocation_ETR = sw.StrtupBookLocation_ETR(cls.winRoot, cls.prefix)
        bookLocation_ETR.render()
        originalMaterialName_ETR = sw.StrtupOriginalMaterialName_ETR(cls.winRoot, cls.prefix)
        originalMaterialName_ETR.render()
        originalMaterialLocation_ETR = sw.StrtupOriginalMaterialLocation_ETR(cls.winRoot, cls.prefix)
        originalMaterialLocation_ETR.render()

        addbook_BTN = sw.AddBook_BTN(cls.winRoot, cls.prefix, None)
        addbook_BTN.render()

        # assign the keys
        cls._bindKeys()
        
        # run the tk
        cls.winRoot.mainloop()

    @classmethod
    def _bindKeys(cls):
        cls.winRoot.bind("<Escape>", lambda e: cls.winRoot.destroy())
        cls.winRoot.bind("<Return>", lambda e: cls.winRoot.destroy())

