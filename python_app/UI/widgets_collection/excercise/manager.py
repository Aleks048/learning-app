import UI.widgets_collection.excercise.excercise as exw

import UI.widgets_manager as wm
import file_system.file_system_facade as fsf
import settings.facade as sf
import _utils._utils_main as _u
import UI.widgets_collection.excercise.excercise as exw


class LayoutManagers:

    class ExcerciseLayout(wm.MenuLayout_Interface):
        prefix = "_ExcerciseLayout_"
        subsection = _u.Token.NotDef.str_t
        imIdx = _u.Token.NotDef.str_t

        def __init__(self, winRoot):
            appDimensions = [720, 800, 0, 0]
            super().__init__(winRoot, appDimensions)
            self.excerciseImage = exw.ExcerciseImage(winRoot, self.prefix)
            self.addWidget(self.excerciseImage)
            self.excercise_BOX = exw.Excercise_BOX(winRoot, self.prefix)
            self.addWidget(self.excercise_BOX)
            self.addExcerciseLine_BTN = exw.AddExcerciseLine_BTN(winRoot, self.prefix)
            self.addWidget(self.addExcerciseLine_BTN)
            hideExcerciseWindow_BTN = exw.HideExcerciseWindow_BTN(winRoot, self.prefix)
            self.addWidget(hideExcerciseWindow_BTN)
            self.pasteGlLink_BTN = exw.PasteGlLink_BTN(winRoot, self.prefix)
            self.addWidget(self.pasteGlLink_BTN)
            addExcerciseLine_ETR = exw.AddExcerciseLine_ETR(winRoot, self.prefix)
            self.addWidget(addExcerciseLine_ETR)
            self.moveTOCtoExcerciseEntry_BTN = exw.MoveTOCtoExcerciseEntry_BTN(winRoot, self.prefix)
            self.addWidget(self.moveTOCtoExcerciseEntry_BTN)
            hideAllETRsWindow_BTN = exw.HideAllETRsWindow_BTN(winRoot, self.prefix)
            self.addWidget(hideAllETRsWindow_BTN)

            self.addExcerciseLine_BTN.addListenerWidget(addExcerciseLine_ETR)
            addExcerciseLine_ETR.addListenerWidget(self.addExcerciseLine_BTN)
            self.addExcerciseLine_BTN.addListenerWidget(self.excercise_BOX)
            hideAllETRsWindow_BTN.addListenerWidget(self.excercise_BOX)

            winRoot.setGeometry(*self.appDimensions)
        def show(self):
            self.excerciseImage.subsection = self.subsection
            self.excerciseImage.entryIdx = self.imIdx

            self.pasteGlLink_BTN.subsection = self.subsection
            self.pasteGlLink_BTN.imIdx = self.imIdx

            self.moveTOCtoExcerciseEntry_BTN.subsection = self.subsection
            self.moveTOCtoExcerciseEntry_BTN.imIdx = self.imIdx

            self.addExcerciseLine_BTN.subsection = self.subsection
            self.addExcerciseLine_BTN.imIdx = self.imIdx

            self.excercise_BOX.subsection = self.subsection
            self.excercise_BOX.imIdx = self.imIdx

            super().show()

            # resize the solution box in respect to the size of the excercise image
            self.excerciseImage.widgetObj.update()
            self.excercise_BOX.canvas.configure(height = 730 - 20 - self.excerciseImage.widgetObj.winfo_height())
            self.excercise_BOX.canvas.update()

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
        