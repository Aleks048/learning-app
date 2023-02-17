import tkinter as tk

import _utils._utils_main as _u
import layouts.layouts_manager as lm

import UI.widgets_manager as wm
import UI.widgets_utils as wu
import UI.widgets_wrappers as ww

import UI.widgets_collection.main.math.layouts.common as com
import UI.widgets_collection.main.math.layouts.common as ml
import UI.widgets_collection.main.math.layouts.common as sl
import data.constants as dc

class LayoutManagers:
    class _Main(wm.MenuLayout_Interface):
        prefix = "_mainLayout"
        name = __name__
        def __init__(self, winRoot):
            monitorSize = dc.MonitorSize.getData()
            monHalfWidth = int(monitorSize[0] / 2)
            appDimensions = [monHalfWidth, 90, monHalfWidth, 0]
            print(appDimensions)
            super().__init__(winRoot, appDimensions)


            layouts_OM = com.Layouts_OM(winRoot, self.prefix)
            self.addWidget(layouts_OM)


            #
            # layout: 
            #
            # layoutOM = LayoutsMenus._commonWidgets.getOptionsMenu_Layouts(winMainRoot, cls.classPrefix)
            # layoutOM.grid(column = 1, row = 0, padx = 0, pady = 0)

    class _Section(wm.MenuLayout_Interface):
        prefix = "_sectionLayout"
        name = __name__
        @classmethod
        def __init__(self, winRoot):
            pass
    
    @classmethod
    def listOfLayouts(cls):
        results = []
        for attrname in dir(cls):
            obj = getattr(cls, attrname)
            if isinstance(obj, type) and issubclass(obj, wm.MenuLayout_Interface):
                results.append(obj)
        return results

class MathMenuManager(wm.MenuManager_Interface):
    prefix = "_MainMathMenu_"

    @classmethod
    def createMenu(cls):
        super().createMenu()

        cls.winRoot = com.MainMenuRoot(0, 0)

        for lm in LayoutManagers.listOfLayouts():
            cls.layouts.append(lm(cls.winRoot))
        
        cls.currLayout = cls.layouts[0]