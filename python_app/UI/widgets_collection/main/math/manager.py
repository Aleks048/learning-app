import tkinter as tk

import _utils._utils_main as _u
import layouts.layouts_manager as lm

import UI.widgets_manager as wm
import UI.widgets_utils as wu
import UI.widgets_wrappers as ww

import UI.widgets_collection.main.math.layouts.common as com
import UI.widgets_collection.main.math.layouts.common as ml
import UI.widgets_collection.main.math.layouts.common as sl

import UI.widgets_collection.main.manager as wmm




class LayoutManager_Interface(wmm.MainMenuManager):
    pass

class LayoutManagers:
    class _Main(LayoutManager_Interface):
        def addWidgets(rootWidget):           
            mon_width, _ = _u.getMonitorSize()
            pyAppDimensions = [int(mon_width / 2), 90]

            

            #
            # layout: 
            #
            # layoutOM = LayoutsMenus._commonWidgets.getOptionsMenu_Layouts(winMainRoot, cls.classPrefix)
            # layoutOM.grid(column = 1, row = 0, padx = 0, pady = 0)

    class _Section(LayoutManager_Interface):
        def addWidgets(rootWidget):
            pass
    
    listOfManagers = [_Main, _Section]

class MathMenuManager(wmm.MainMenuManager):
    @classmethod
    def createMenu(cls):
        super().createMenu()

        cls.winRoot = com.MainMenuRoot(0, 0)


        for lm in LayoutManagers.listOfManagers:
            lm.addWidgets(cls.winRoot)
        # wc.LayoutsMenus.SectionLayoutUI.addWidgets(cls.winRoot)
        # wu.hideAllWidgets(cls.winRoot)
        # wc.SectionsUI.setSectionsUI(cls.winRoot)
        # cls.LayoutManagers.Main.addWidgets(cls.winRoot)
        # _u.Settings.UI.showMainWidgetsNext = False

        #set Layout
        # menuDimensions = wc.LayoutsMenus.MainLayoutUI.pyAppDimensions
        # lm.Wr.MainLayout.set(cls.winRoot, *menuDimensions)

        # cls.winRoot.mainloop()

    def show(self):
        pass

    @classmethod
    def _bindKeys(cls):
        pass