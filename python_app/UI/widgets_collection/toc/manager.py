import UI.widgets_collection.toc.toc as tocw

import UI.widgets_manager as wm
import UI.widgets_collection.common as comw


class LayoutManagers:
    class TOCLayout(wm.MenuLayout_Interface):
        prefix = "_TOCLayout_"

        def __init__(self, winRoot):
            appDimensions = [700, 500, 200, 200]
            super().__init__(winRoot, appDimensions)

            tocBox = comw.TOC_BOX(winRoot, self.prefix, True)
            tocBox.populateTOC()
            self.addWidget(tocBox)

            hide_BTN = tocw.Hide_BTN(winRoot, self.prefix)
            self.addWidget(hide_BTN)

            filter_ETR = tocw.Filter_ETR(winRoot, self.prefix)
            self.addWidget(filter_ETR)

            filter_ETR.addListenerWidget(tocBox)

            winRoot.setGeometry(*self.appDimensions)

    @classmethod
    def listOfLayouts(cls):
        results = []
        for attrname in dir(cls):
            obj = getattr(cls, attrname)
            if isinstance(obj, type) and issubclass(obj, wm.MenuLayout_Interface):
                results.append(obj)
        return results

class TOCManager(wm.MenuManager_Interface):
    def __init__(self):
        winRoot = tocw.TOCRoot(100, 100)
        layouts = []
        for lm in LayoutManagers.listOfLayouts():
            layouts.append(lm(winRoot))
            
        currLayout = layouts[0]
        
        super().__init__(winRoot,
                        layouts,
                        currLayout)
        