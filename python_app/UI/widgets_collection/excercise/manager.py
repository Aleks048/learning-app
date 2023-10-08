import UI.widgets_collection.excercise.excercise as exw

import UI.widgets_manager as wm


class LayoutManagers:
    class ExcerciseLayout(wm.MenuLayout_Interface):
        prefix = "_TOCLayout_"

        def __init__(self, winRoot):
            appDimensions = [720, 800, 0, 0]
            super().__init__(winRoot, appDimensions)


            winRoot.setGeometry(*self.appDimensions)

    @classmethod
    def listOfLayouts(cls):
        results = []
        for attrname in dir(cls):
            obj = getattr(cls, attrname)
            if isinstance(obj, type) and issubclass(obj, wm.MenuLayout_Interface):
                results.append(obj)
        return results

class ExcerciseManager(wm.MenuManager_Interface):
    def __init__(self):
        winRoot = exw.ExcerciseRoot(50, 50)
        layouts = []
        for lm in LayoutManagers.listOfLayouts():
            layouts.append(lm(winRoot))
            
        currLayout = layouts[0]
        
        super().__init__(winRoot,
                        layouts,
                        currLayout)
        