import UI.widgets_collection.excerciseSolution.excerciseSolution as esln

import UI.widgets_manager as wm
import file_system.file_system_facade as fsf
import settings.facade as sf
import _utils._utils_main as _u

class LayoutManagers:
    class ImagesLayout(wm.MenuLayout_Interface):
        def __init__(self, winRoot):
            self.prefix = "_ImagesLayout_"
            self.subsection = _u.Token.NotDef.str_t
            self.imIdx = _u.Token.NotDef.str_t

            appDimensions = [720, 800, 720, 0]
            super().__init__(winRoot, appDimensions)
            self.hideExcerciseSolutionWindow_BTN = \
                esln.HideExcerciseSolutionWindow_BTN(winRoot, self.prefix)
            self.addWidget(self.hideExcerciseSolutionWindow_BTN)
            self.excerciseSolutionLabel = \
                esln.ExcerciseSolutionLabel(winRoot, self.prefix)
            self.addWidget(self.excerciseSolutionLabel)

            self.addFromClipbordExcerciseSolutionWindow_BTN = \
                esln.AddFromClipbordExcerciseSolutionWindow_BTN(winRoot, self.prefix)
            self.addWidget(self.addFromClipbordExcerciseSolutionWindow_BTN)
            self.addFromClipbordExcerciseSolutionWindow_BTN.addListenerWidget(self.excerciseSolutionLabel)

            self.addScreenshotExcerciseSolutionWindow_BTN = \
                esln.AddScreenshotExcerciseSolutionWindow_BTN(winRoot, self.prefix)
            self.addWidget(self.addScreenshotExcerciseSolutionWindow_BTN)
            self.addScreenshotExcerciseSolutionWindow_BTN.addListenerWidget(self.excerciseSolutionLabel)

            winRoot.setGeometry(*self.appDimensions)

        def show(self):
            self.excerciseSolutionLabel.subsection = self.subsection
            self.excerciseSolutionLabel.imIdx = self.imIdx
            self.addFromClipbordExcerciseSolutionWindow_BTN.subsection = self.subsection
            self.addFromClipbordExcerciseSolutionWindow_BTN.imIdx = self.imIdx
            self.addScreenshotExcerciseSolutionWindow_BTN.subsection = self.subsection
            self.addScreenshotExcerciseSolutionWindow_BTN.imIdx = self.imIdx

            super().show()

    @classmethod
    def listOfLayouts(cls):
        results = []
        for attrname in dir(cls):
            obj = getattr(cls, attrname)
            if isinstance(obj, type) and issubclass(obj, wm.MenuLayout_Interface):
                results.append(obj)
        return results

class ExcerciseSolutionManager(wm.MenuManager_Interface):
    imIdx = 0
    def __init__(self):
        winRoot = esln.ExcerciseSolutionRoot(50, 50)
        layouts = []
        for lm in LayoutManagers.listOfLayouts():
            layouts.append(lm(winRoot))
            
        self.subsection = fsf.Data.Book.currSection
        currLayout = layouts[0]
        currLayout.subsection = self.subsection
        
        super().__init__(winRoot,
                        layouts,
                        currLayout)
        winRoot.hide()
    def show(self, subsection, imIdx):
        self.layouts[0].subsection = subsection
        self.layouts[0].imIdx = imIdx
        return super().show()