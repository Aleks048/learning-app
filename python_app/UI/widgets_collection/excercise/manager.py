import UI.widgets_collection.excercise.excercise as exw

import UI.widgets_manager as wm
import file_system.file_system_facade as fsf
import settings.facade as sf
import _utils._utils_main as _u
import UI.widgets_collection.excercise.excercise as exw


class LayoutManagers:

    class ExcerciseLayout(wm.MenuLayout_Interface):
        prefix = "_TOCLayout_"
        subsection = _u.Token.NotDef.str_t
        imIdx = _u.Token.NotDef.str_t

        def __init__(self, winRoot):
            appDimensions = [720, 800, 0, 0]
            super().__init__(winRoot, appDimensions)
            self.excerciseImage = exw.ExcerciseImage(winRoot)
            self.addWidget(self.excerciseImage)

            winRoot.setGeometry(*self.appDimensions)
        def show(self):
            self.excerciseImage.subsection = self.subsection
            self.excerciseImage.entryIdx = self.imIdx
            return super().show()

    @classmethod
    def listOfLayouts(cls):
        results = []
        for attrname in dir(cls):
            obj = getattr(cls, attrname)
            if isinstance(obj, type) and issubclass(obj, wm.MenuLayout_Interface):
                results.append(obj)
        return results

class ExcerciseManager(wm.MenuManager_Interface):
    imIdx = 0
    def __init__(self):

        winRoot = exw.ExcerciseRoot(50, 50)
        layouts = []
        for lm in LayoutManagers.listOfLayouts():
            layouts.append(lm(winRoot))
            
        self.subsection = fsf.Data.Book.currSection
        currLayout = layouts[0]
        currLayout.subsection = self.subsection
        
        super().__init__(winRoot,
                        layouts,
                        currLayout)
    def show(self):
        self.layouts[0].subsection = self.subsection
        self.layouts[0].imIdx = self.imIdx
        return super().show()
        