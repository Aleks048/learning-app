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

import UI.widgets_collection.layouts.mathLayouts.mainLayout as icw
import UI.widgets_collection.startup.startup as sw


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



